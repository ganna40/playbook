# tarot - 타로 마스터 루미나

> URL: (로컬 개발 중)
> GitHub: https://github.com/ganna40/tarrot_project

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | AI 타로 상담 (풀스택) |
| **한줄 설명** | 질문 입력 → 카드 선택 → RAG 기반 AI 해석 + 대화형 상담 |
| **타겟** | 타로 상담에 관심 있는 사용자 |
| **테마** | 다크 (네이비 + 골드 + 퍼플) |
| **폰트** | Noto Sans KR (Google Fonts) |

## 기술 스택

> **첫 번째 풀스택 프로젝트.** 프론트+백엔드+DB+LLM+RAG 전부 포함.

### 프론트엔드

| 기술 | 용도 |
|------|------|
| **React 18** | UI 프레임워크 (함수형 컴포넌트) |
| **React Router DOM** | 페이지 라우팅 (/, /reading/:spreadType, /card/:cardId) |
| **Framer Motion** | 애니메이션 (등장, 호버, 카드 뒤집기) |
| **Axios** | HTTP 클라이언트 (API 호출) |
| **순수 CSS + CSS Variables** | 다크 테마 (--accent-gold, --accent-purple) |
| **Noto Sans KR** | Google Fonts 한글 폰트 |

### 백엔드

| 기술 | 용도 |
|------|------|
| **FastAPI** | REST API 서버 |
| **SQLAlchemy (async)** | ORM (비동기) |
| **PostgreSQL + pgvector** | DB + 768차원 벡터 검색 |
| **Ollama** | 로컬 LLM (기본: gemma3:4b) |
| **OpenRouter** | 클라우드 LLM (기본: gpt-4o-mini) |
| **sentence-transformers** | 임베딩 생성 (nomic-embed-text) |
| **Docker Compose** | 컨테이너 오케스트레이션 (DB + Backend) |
| **Pydantic** | 데이터 검증 |
| **httpx** | 비동기 HTTP 클라이언트 (LLM API 호출) |

## 아키텍처

```
[프론트엔드 React]
    ↓ Axios / SSE
[FastAPI 백엔드]
    ├── 가드레일 미들웨어 (민감 주제 필터링)
    ├── 카드 뽑기 (Fisher-Yates 셔플, 역방향 30%)
    ├── RAG 컨텍스트 검색 (pgvector 코사인 유사도)
    │   ├── PKT 원전 (A.E. Waite, 1911)
    │   ├── 타로 마스터 교안 PDF
    │   ├── Knowledge Base JSON
    │   ├── 심리학 고전 (Jung/Freud/James)
    │   └── 상담 기법 자료
    ├── LLM 해석 생성 (Ollama or OpenRouter)
    ├── QA 매니저 (품질 평가 5가지 메트릭)
    ├── 메모리 매니저 (슬라이딩 윈도우 + 자동 요약)
    └── 콜드 리딩 기법 (바넘 효과, 레인보우 루즈)
        ↓
[PostgreSQL + pgvector]
    ├── tarot_cards (78장 + 임베딩)
    ├── card_chunks (RAG 청크 + 임베딩)
    ├── consultation_sessions
    ├── consultation_messages
    └── qa_logs
```

## 화면 흐름

```
HomePage (스프레드 선택: 싱글/쓰리/켈틱/연애/직업)
  → ReadingPage
    → question (질문 입력)
      → selecting (78장 카드에서 선택)
        → revealing (3D 카드 뒤집기 애니메이션)
          → result (AI 해석 + 채팅 인터페이스)
  → CardDetailPage (개별 카드 상세: 정방향/역방향 토글)
```

## 핵심 기능

| 기능 | 설명 |
|------|------|
| **5가지 스프레드** | 싱글(1) / 쓰리(3) / 연애(5) / 직업(5) / 켈틱크로스(10) |
| **78장 타로 덱** | 메이저 22 + 마이너 56 (Wands/Cups/Swords/Pentacles) |
| **RAG 파이프라인** | 5개 소스에서 벡터 검색 → LLM 컨텍스트 주입 |
| **듀얼 LLM** | Ollama(로컬) ↔ OpenRouter(클라우드) 런타임 전환 |
| **SSE 스트리밍** | 실시간 AI 응답 스트리밍 |
| **가드레일** | 8가지 민감 카테고리 필터 + 전문 상담 리소스 안내 |
| **콜드 리딩** | 바넘 효과, 레인보우 루즈, 푸싱 기법 (30% 강도) |
| **QA 매니저** | 공감/관련성/카드정확성/페르소나/안전성 5가지 평가 |
| **메모리 매니저** | 슬라이딩 윈도우(5턴) + 10턴 초과 시 자동 요약 |
| **3D 카드 뒤집기** | CSS perspective + rotateY + backface-visibility |
| **Fisher-Yates 셔플** | 진정한 무작위 순열 (7회 반복) |
| **역방향 확률** | 30% 확률로 카드 역방향 |
| **마크다운 렌더링** | AI 응답의 ##, **, _ 패턴을 React 엘리먼트로 변환 |
| **대화형 채팅** | 리딩 결과 기반 추가 질문 가능 |

## 페르소나: 타로 마스터 루미나

```
- 30년 경력 전문 타로 심리상담사
- 한국어 전용 (영어/외국어 절대 금지)
- YES/NO 판단 우선 (애매한 표현 최소화)
- 마크다운/테이블 사용 금지 (자연스러운 대화체)
- 출처 언급 금지 ("프로이트에 따르면" → "제 경험상")
- 칼 로저스 상담 기법 기반 (수용적 존중, 공감적 이해)
```

## DB 스키마

```
PostgreSQL + pgvector
├── tarot_cards (78장)
│   ├── name, name_kr, suit, number
│   ├── image_description, core_symbolism
│   ├── upright_meaning, reversed_meaning
│   ├── scenario_interpretations (JSONB)
│   └── embedding (Vector 768)
├── card_chunks (RAG)
│   ├── card_id, chunk_type, content
│   ├── metadata (JSONB)
│   └── embedding (Vector 768)
├── consultation_sessions
├── consultation_messages
└── qa_logs (품질 평가)
```

## 프로젝트 구조

```
tarrot_project/
├── docker-compose.yml          # DB + Backend 컨테이너
├── frontend/
│   ├── package.json            # React 18, Framer Motion, Axios
│   ├── public/
│   │   ├── index.html          # Noto Sans KR 로드
│   │   └── cards/              # 타로 카드 이미지
│   └── src/
│       ├── App.js              # React Router (3개 라우트)
│       ├── index.css           # CSS Variables 다크 테마
│       ├── App.css             # 글로벌 애니메이션 (fadeIn, glow, cardFlip, shimmer)
│       ├── pages/
│       │   ├── HomePage.js     # 랜딩 (스프레드 선택 그리드)
│       │   ├── ReadingPage.js  # 핵심 (질문→선택→공개→결과+채팅)
│       │   └── CardDetailPage.js # 카드 상세 (정방향/역방향)
│       ├── components/
│       │   ├── Header.js       # 네비게이션 (Glassmorphism)
│       │   └── TarotCard.js    # 3D 카드 (perspective, rotateY)
│       └── services/
│           └── api.js          # Axios + SSE 스트리밍
├── backend/
│   ├── Dockerfile              # Python 3.11-slim
│   ├── requirements.txt        # FastAPI, SQLAlchemy, pgvector, Ollama
│   ├── app/
│   │   ├── main.py             # FastAPI 진입점 + CORS + 가드레일
│   │   ├── config.py           # 환경변수 설정 (LLM, RAG, 타로)
│   │   ├── models/
│   │   │   ├── database.py     # SQLAlchemy 모델 (5개 테이블)
│   │   │   └── tarot_deck.py   # 78장 덱 (셔플, 스프레드)
│   │   ├── routers/
│   │   │   └── consultation.py # API 엔드포인트 (10개)
│   │   ├── services/
│   │   │   ├── llm_service.py  # Ollama/OpenRouter 듀얼 LLM
│   │   │   ├── rag_service.py  # pgvector 벡터 검색
│   │   │   ├── guardrail.py    # 민감 주제 필터링
│   │   │   ├── qa_manager.py   # 품질 평가 + 콜드 리딩
│   │   │   ├── memory_manager.py # 대화 컨텍스트 관리
│   │   │   ├── pkt_parser.py   # PKT 원전 파싱
│   │   │   └── psychology_parser.py # 심리학 텍스트 파싱
│   │   └── utils/
│   │       ├── prompts.py      # 시스템 프롬프트 + 프롬프트 빌더
│   │       └── parse_pkt.py    # PKT 파싱 유틸리티
│   └── scripts/
│       ├── init_postgres.sql   # pgvector 확장 활성화
│       └── *.py                # 데이터 임포트 스크립트들
└── data/
    ├── raw/                    # 원본 텍스트 (PKT, 심리학)
    ├── parsed/                 # 파싱된 JSON
    ├── translated/             # 한국어 번역
    └── scenarios/              # 시나리오별 해석
```

## 기존 앱과의 차이

| 항목 | 기존 앱 (salary, pong 등) | tarot |
|------|---------------------------|-------|
| 아키텍처 | 프론트엔드만 (SPA) | 풀스택 (React + FastAPI + DB) |
| 백엔드 | 없음 | FastAPI + PostgreSQL + pgvector |
| AI/LLM | 없음 | Ollama / OpenRouter (RAG 파이프라인) |
| 데이터 | JSON/인라인 | PostgreSQL + 벡터 임베딩 |
| 배포 | EC2 정적 파일 | Docker Compose |
| CSS | Tailwind/CDN | 순수 CSS + CSS Variables |
| 프레임워크 | 바닐라 JS | React 18 |
| 공유 | 카카오톡/URL | 없음 |

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | /api/consultation | 풀 타로 상담 (스프레드 + AI 해석) |
| POST | /api/quick-reading | 싱글 카드 퀵 리딩 |
| POST | /api/consultation/stream | SSE 스트리밍 상담 |
| POST | /api/chat | 대화형 추가 질문 |
| GET | /api/spreads | 스프레드 목록 |
| GET | /api/cards | 전체 카드 목록 |
| GET | /api/cards/:cardId | 카드 상세 |
| GET | /api/ollama/status | Ollama 상태 |
| POST | /api/llm/switch/:provider | LLM 프로바이더 전환 |

## AI에게 비슷한 거 만들게 하려면

```
playbook의 tarot 레퍼런스를 보고
"AI 사주/운세 상담"을 만들어줘.
React + FastAPI + PostgreSQL + pgvector + Ollama.
- tarot과 동일한 아키텍처
- RAG 파이프라인 (사주 원전 + 운세 해석 데이터)
- 가드레일 + 메모리 매니저 포함
- Docker Compose 배포
```
