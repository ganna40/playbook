# human2 - 고독한 나르시시스트 (페르소나 RAG 챗봇)

> GitHub: https://github.com/ganna40/human2

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | AI 챗봇 (페르소나 복제 RAG) |
| **한줄 설명** | 카카오톡 4.69M 메시지 → ETL → 벡터DB → 페르소나 재현 챗봇 |
| **타겟** | 특정 인물의 말투/성격을 재현한 챗봇 |
| **테마** | - (텔레그램 봇) |
| **폰트** | - |

## 모듈 조합

```
LLM + RAG + TELEGRAM + PostgreSQL/pgvector + Redis + LangChain
```

## 핵심 아키텍처

```
[오프라인: ETL 파이프라인]
카톡 로그 (1.txt~6.txt, 260MB, 469만 메시지)
    ↓ 정규식 파싱 ([이름] [시간] 메시지)
    ↓ 세션 청킹 (1시간 갭, 최소 3메시지)
    ↓ Ollama 지능 추출 (요약/토픽/태도)
    ↓ ko-sroberta 임베딩 (768d, GPU)
    ↓ PostgreSQL + pgvector 저장 (2,068세션)

[런타임: RAG 파이프라인]
텔레그램 메시지 수신
    ↓ Redis 단기기억 (최근 10턴, 24시간 TTL)
    ↓ pgvector 장기기억 (코사인 유사도 top-5)
    ↓ 7단계 동적 프롬프트 빌더
    ↓ Ollama (exaone3.5:7.8b) 응답 생성
    ↓ 응답 정제 (태그/마크다운/AI접두사 제거)
    ↓ 청크 전송 (0.5초 딜레이 + 타이핑 효과)
```

## 7단계 동적 프롬프트 빌더

```
Step 1: 베이스 페르소나 (핵심 성격 + 말투 규칙)
Step 2: 태도 주입 (비판적/친근/중립 모드)
Step 3: 컨텍스트 주입 (clean_content 기반 과거 대화)
Step 4: Few-Shot 주입 (페르소나 발화만 추출, top-3 세션)
Step 5: 제약조건 (AI 말투 금지, 설명체 금지, 줄수 제한)
Step 6: 대화 히스토리 (Redis 최근 10턴)
Step 7: 현재 쿼리 (사용자 메시지 + 화자 컨텍스트)
```

## 특수 기능

| 기능 | 설명 |
|------|------|
| **페르소나 복제** | 카톡 대화에서 특정 인물의 말투/성격/지식 재현 |
| **듀얼 메모리** | Redis(단기, 24h TTL) + pgvector(장기, 2,068세션) |
| **태도 기반 응답** | 과거 대화의 감정 태도에 따라 응답 모드 전환 |
| **Few-Shot 학습** | 실제 발화 패턴을 프롬프트에 주입 |
| **클린 컨텐츠** | raw_text/clean_content/persona_content 3중 저장 |
| **DB 기반 신원** | /iam으로 텔레그램→페르소나 매핑 (v3) |
| **화자 분석** | LLM이 화자별 성격 설명 자동 생성 |
| **청크 전송** | 0.5초 딜레이로 타닥타닥 타이핑 효과 |
| **ETL 파이프라인** | 카톡 로그 파싱 → 세션 청킹 → 지능 추출 → 임베딩 → DB |
| **응답 정제** | AI 접두사, 태그, 마크다운 자동 제거 |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| Ollama (exaone3.5:7.8b) | 한국어 특화 LLM (지능 추출 + 응답 생성) |
| PostgreSQL + pgvector | 벡터 DB (768d 임베딩, HNSW/IVFFlat) |
| Redis 7 | 단기 대화 기억 (24시간 TTL) |
| sentence-transformers | ko-sroberta-multitask 임베딩 (768d) |
| python-telegram-bot 21 | 텔레그램 봇 (폴링) |
| LangChain | LLM 워크플로우 오케스트레이션 |
| asyncpg | PostgreSQL 비동기 드라이버 |
| httpx | Ollama 비동기 HTTP 호출 |
| CUDA 12.6 + PyTorch | RTX 4060 Ti GPU 가속 (임베딩) |

## 텔레그램 커맨드

| 커맨드 | 기능 |
|--------|------|
| `/start` | "뭐\n할말잇으면말해" (캐릭터 인사) |
| `/help` | 사용법 + 커맨드 목록 |
| `/iam <닉네임>` | 텔레그램 ID → 페르소나 연결 (v3) |
| `/whoami` | 내 페르소나 정보 |
| `/members` | 등록된 페르소나 목록 (10+메시지) |

## DB 스키마

```
chat_memory (2,068 rows)
├── session_id     — 세션 UUID (8자리)
├── raw_text       — 원본 ([이름] [시간] 메시지)
├── clean_content  — 순수 발화만 (v2)
├── summary        — LLM 추출 요약
├── topics         — JSONB 키워드 배열
├── attitude       — 감정 태도 (비판적/친근/중립)
├── metadata       — JSONB (msg_count, participants, persona_content)
├── embedding      — vector(768) pgvector
└── source_file    — "1.txt" ~ "6.txt"

personas (v3)
├── name, description, msg_count

user_mappings (v3)
├── telegram_id → persona_id 연결
```

## ETL 파이프라인 상세

```python
# 1. 카톡 로그 파싱 (정규식)
pattern = r'^\[(.+?)\]\s*\[(오전|오후)\s*(\d{1,2}):(\d{2})\]\s*(.+)$'

# 2. 세션 청킹 (1시간 갭)
sessions = chunk_into_sessions(messages, gap_minutes=60, min_messages=3)

# 3. 지능 추출 (Ollama, temp=0.1)
{summary, topics[], attitude} = extract_intelligence(session)

# 4. 임베딩 (ko-sroberta, GPU, batch=32)
embedding = model.encode(session.text_for_embedding(), normalize=True)

# 5. pgvector 저장 + 인덱스
# <100 rows: HNSW, ≥100 rows: IVFFlat
```

## 프로젝트 구조

```
human2/
├── config.py              # PG, Redis, Ollama, Telegram 설정
├── etl_pipeline.py        # ETL: 파싱→청킹→추출→임베딩→저장
├── rag_core.py            # RAG: 하이브리드 검색 + 7단계 프롬프트 빌더
├── bot_server.py          # 텔레그램 봇 서버 (폴링)
├── init.sql               # PostgreSQL 스키마
├── migrate_v3.py          # v3 마이그레이션 (personas + user_mappings)
├── update_intelligence.py # 백그라운드 지능 보강
├── requirements.txt
├── 1.txt ~ 6.txt          # 카톡 로그 원본 (~260MB)
├── architecture.html      # 비주얼 아키텍처 문서
└── architecture.md        # 기술 아키텍처 문서
```

## 핵심 통계

| 항목 | 수치 |
|------|------|
| 파싱된 메시지 | 4,689,996개 |
| 세션 청크 | 2,068개 |
| 임베딩 차원 | 768d (ko-sroberta) |
| 원본 데이터 | ~260MB (6개 파일) |
| RAG Top-K | 5 |
| Redis TTL | 24시간 |
| 대화 히스토리 | 최근 10턴 |
| GPU | RTX 4060 Ti (CUDA 12.6) |

## AI에게 비슷한 거 만들게 하려면

```
playbook의 human2 레퍼런스를 보고
"카톡 페르소나 챗봇"을 만들어줘.
LLM + RAG + TELEGRAM 조합.
카톡 로그 ETL → pgvector 저장 → 7단계 프롬프트 빌더.
듀얼 메모리: Redis(단기) + pgvector(장기).
Ollama(exaone3.5:7.8b) + ko-sroberta(768d) 임베딩.
```
