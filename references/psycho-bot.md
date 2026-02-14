# psycho-bot - AI 심리 상담 챗봇 (마음벗 MindMate)

> GitHub: https://github.com/ganna40/psycho_bot
> 플랫폼: Telegram Bot / REST API / Discord (예정)

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | AI 심리 상담 챗봇 (텔레그램/웹) |
| **한줄 설명** | 심리학 기반 공감적 AI 동반자 — 상담·교육·대화 3가지 모드 |
| **타겟** | 정서적 지지가 필요한 일반 사용자, 심리학 관심자 |
| **테마** | (백엔드 전용, UI 없음) |
| **폰트** | (백엔드 전용) |

## 모듈 조합

```
LLM + RAG + TELEGRAM
```

**추가 스택**: FastAPI, PostgreSQL/pgvector, Redis, sentence-transformers, Alembic, Docker Compose

## 아키텍처

```
[텔레그램/디스코드/웹]
        │
        ▼
   FastAPI REST API
        │
  ┌─────┼─────────────────────────────┐
  │     │  메시지 분석 파이프라인       │
  │  위기감지 → 주제분류 → 모드감지    │
  │              → 감정분석             │
  └─────┼─────────────────────────────┘
        │
  ┌─────┼─────────────────────────────┐
  │  컨텍스트 수집                      │
  │  RAG검색 + 대화요약 + 유저프로필   │
  │  + 자기인식 엔진                    │
  └─────┼─────────────────────────────┘
        │
        ▼
   프롬프트 조합 → LLM 호출 → 응답
        │
  ┌─────┼─────────────────────────────┐
  │  후처리 & 학습                      │
  │  DB저장 + 학습DB + 프로필 업데이트 │
  └───────────────────────────────────┘
```

## 핵심 기능

| 기능 | 설명 |
|------|------|
| **5가지 대화 모드** | 상담사(counselor), 선생님(teacher), 친구(friend), 하이브리드(hybrid), 짧은답변(short) |
| **3단계 주제 분류** | 키워드매칭 → 패턴매칭 → 학습DB 유사도 (7개 주제: MBTI, 관계, 감정, 진로, 자기이해, 임상, 정신분석) |
| **3단계 위기 감지** | Level 1(모니터링) → Level 2(주의) → Level 3(즉시 개입, 1393 안내) |
| **자기인식 엔진** | EXAONE-Deep으로 사용자 심리상태 추적 (기분, 핵심욕구, 스트레스 트리거) |
| **학습 DB** | 대화마다 주제분류 결과를 저장 → 키워드/패턴 자동 추출 → 분류 정확도 개선 |
| **사용자 요청 감지** | "반말해줘", "짧게", "질문하지마" 등 스타일 요청을 파싱해서 JSONB로 저장 |
| **감정 분류** | 12+ 감정 키워드 기반, 강도 1~5 계산 (수식어 보정) |
| **대화 요약** | 과거 대화 컨텍스트를 LLM으로 요약해서 세션 간 연결 |
| **그룹채팅 지원** | 그룹 내 개인별 세션/프로필/감정 추적 |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| **FastAPI** | 비동기 REST API + SSE 스트리밍 |
| **PostgreSQL + pgvector** | 벡터 DB (1024차원 임베딩 검색) |
| **sentence-transformers** | intfloat/multilingual-e5-large (1024d) 로컬 임베딩 |
| **Ollama** | exaone3.5:7.8b (한국어 특화 로컬 LLM) |
| **OpenAI API** | GPT-4o/4o-mini (클라우드 LLM) |
| **GGUF** | llama-cpp-python 로컬 추론 |
| **python-telegram-bot 21** | 텔레그램 봇 (개인/그룹 채팅) |
| **Redis 7** | 임베딩/RAG결과/프로필 캐시 |
| **Alembic** | DB 마이그레이션 |
| **Docker Compose** | PostgreSQL + Redis 컨테이너 |
| **SQLAlchemy 2.0 (async)** | 비동기 ORM |

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/chat` | 일반 채팅 (블로킹) |
| POST | `/api/chat/stream` | SSE 실시간 스트리밍 |
| POST | `/api/chat/awareness` | 자기인식 모드 (딥 추론) |
| POST | `/api/sessions` | 세션 생성 |
| GET | `/api/sessions/{id}` | 세션 조회 |
| POST | `/api/sessions/{id}/end` | 세션 종료 |
| POST | `/api/user/profile` | 프로필 저장/수정 |
| GET | `/api/user/profile/{id}` | 프로필 조회 |
| GET | `/api/llm/status` | LLM 상태 조회 |
| POST | `/api/llm/switch` | 런타임 LLM 전환 |

## DB 스키마 (18+ 테이블)

```
Core:
├── users                    # 사용자
├── sessions                 # 대화 세션
├── messages                 # 메시지 (role, mode, topic_analysis, emotion_analysis)
│
Topic Router:
├── topic_keywords           # 주제 키워드 (is_exclusive, weight)
├── topic_patterns           # 주제 패턴 (regex, weight)
├── conversation_learning    # 학습 DB (embedding Vector(1024), is_verified)
│
RAG:
├── rag_documents            # 지식베이스 (embedding Vector(1024), metadata JSONB)
│
User:
├── user_profiles            # 프로필 (preferences JSONB, request JSONB)
├── emotion_logs             # 감정 기록 (crisis_level 0~3)
│
Psychology:
├── concepts                 # 심리학 개념 (name_ko, name_en, category)
├── concept_metaphors        # 개념별 비유 모음
│
Multi-Chat:
├── chat_rooms               # 채팅방 (private/group/broadcast)
├── chat_room_members        # 방 멤버 (owner/admin/member)
├── room_state               # 방 상태 (current_mood, crisis_level, ai_context)
├── room_messages            # 방 메시지 (reply_to, emotion_analysis)
│
Social:
├── relations                # 관계 (friend/family/colleague/mentor 등)
```

## RAG 지식베이스 구조

```
rag_data/
├── 01_counseling_techniques/    # 적극적 경청, 공감반영, 개방형 질문, 감정타당화
├── 02_conversation_examples/    # 좋은/나쁜 대화 예시 50+
├── 03_concepts/                 # 그림자, 투사, 방어기제, 한국적 정서
├── 04_mbti/                     # 16개 유형 + 인지기능
├── 05_emotions/                 # 한국어 감정 휠
├── 06_metaphors/                # 개념별 비유 모음
└── 07_crisis/                   # 위기 프로토콜 + 한국 위기기관
```

## 프롬프트 구조

```
시스템 프롬프트 (system.md)
├── 정체성: "따뜻하고 깊이 있는 심리 동반자"
├── 핵심 가치: 무조건적 긍정적 존중, 공감, 진정성, 안전
├── 변수 치환: {user_name}, {current_mode}, {user_request_detail}
│
모드별 프롬프트 (counselor.md / teacher.md / friend.md / short.md)
├── 상담사: 감정 우선, 질문으로 성찰, 조언은 요청 시에만
├── 선생님: 쉬운 말, 비유 필수, 구조화 (핵심→비유→예시→적용)
├── 친구: 반말, 캐주얼, 존댓말 금지
├── 짧은답변: 2~3문장, 질문 금지
│
컨텍스트 주입
├── RAG 검색 결과
├── 대화 요약 (이전 세션)
├── 사용자 프로필 & 요청사항
└── 위기 가이드 (해당 시)
```

## 프로젝트 구조

```
psycho_bot/
├── MINDMATE_UNIFIED_SPEC.md      # 1000줄+ 마스터 스펙
├── LLM_SWITCHING_GUIDE.md        # LLM 전환 가이드
├── Modelfile                      # Ollama 모델 설정
│
└── mindmate/
    ├── app/
    │   ├── main.py               # FastAPI 엔트리
    │   ├── config.py             # 설정 (18개 환경변수)
    │   ├── models/
    │   │   ├── database.py       # DB 엔진, 세션 팩토리
    │   │   └── schemas.py        # 18+ SQLAlchemy 모델
    │   ├── routers/
    │   │   ├── chat.py           # 채팅 엔드포인트 (700줄+)
    │   │   ├── sessions.py       # 세션 CRUD
    │   │   └── feedback.py       # 피드백 수집
    │   ├── services/
    │   │   ├── crisis.py         # 3단계 위기감지
    │   │   ├── topic_router.py   # 3단계 주제분류
    │   │   ├── mode_detector.py  # 5모드 감지
    │   │   ├── emotion.py        # 감정분류
    │   │   ├── rag.py            # 벡터 검색+캐시
    │   │   ├── embedding.py      # E5-large + Redis 캐시
    │   │   ├── llm.py            # 멀티 프로바이더 LLM
    │   │   ├── learning_db.py    # 대화 학습
    │   │   ├── user_profile.py   # 프로필 관리
    │   │   ├── request_detector.py    # 요청 파싱
    │   │   ├── self_awareness.py      # 자기인식 엔진
    │   │   ├── context_manager.py     # 컨텍스트 합성
    │   │   ├── conversation_summarizer.py  # 대화 요약
    │   │   ├── cache.py               # Redis 캐시
    │   │   └── dynamic_prompt_builder.py  # 프롬프트 조합
    │   └── prompts/
    │       ├── system.md         # 베이스 시스템 프롬프트
    │       ├── counselor.md      # 상담사 모드
    │       ├── teacher.md        # 선생님 모드
    │       ├── friend.md         # 친구 모드
    │       └── short.md          # 짧은답변 모드
    │
    ├── rag_data/                 # 심리학 지식베이스 (7개 카테고리)
    ├── scripts/                  # 초기화/마이그레이션 스크립트
    ├── tests/                    # 테스트 스위트
    ├── telegram_bot.py           # 텔레그램 봇 메인
    ├── docker-compose.yml        # PostgreSQL + Redis
    └── requirements.txt          # 20+ 의존성
```

## tarot과 비교

| 항목 | tarot | psycho-bot |
|------|-------|------------|
| **프론트엔드** | React 18 | 없음 (API 전용) |
| **LLM** | Ollama/OpenRouter | Ollama/OpenAI/GGUF |
| **임베딩** | nomic-embed-text (768d) | multilingual-e5-large (1024d) |
| **캐시** | 없음 | Redis 7 |
| **플랫폼** | 웹 브라우저 | 텔레그램/디스코드/REST |
| **RAG 소스** | 타로 카드/해석/심리학 | 상담기법/개념/비유/위기/MBTI |
| **NLP 파이프라인** | 가드레일만 | 위기→주제→모드→감정 4단계 |
| **학습** | 없음 | 대화에서 키워드/패턴 자동 추출 |
| **세션** | 웹 기반 | 텔레그램 개인/그룹 세션 |
| **DB 규모** | 5 테이블 | 18+ 테이블 |

## AI에게 비슷한 거 만들게 하려면

```
playbook의 psycho-bot 레퍼런스를 보고
"{새 봇 이름}" 텔레그램 봇을 만들어줘.

LLM + RAG + TELEGRAM 조합.

FastAPI 백엔드 + PostgreSQL/pgvector + Ollama.
텔레그램 봇으로 {주제} 상담.
주제 분류 + 감정 분석 + 위기 감지 포함.
대화 모드: [상담/교육/친구] 중 선택.
```
