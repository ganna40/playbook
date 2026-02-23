# saju - 사주팔자 AI 풀이 대시보드

> URL: http://localhost:8888 (로컬 전용)
> 소스: C:\Users\ganna\saju-app\dashboard.py (단일 파일)

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | AI 풀이 대시보드 (만세력→격국분석→LLM해석) |
| **한줄 설명** | 생년월일시 입력하면 사주팔자 + 대운/세운 + AI 9개 카테고리 해석 |
| **타겟** | 사주에 관심 있는 일반인 |
| **테마** | 다크 (금/적색 악센트) |
| **폰트** | Noto Serif KR + Nanum Myeongjo (Google Fonts) |

## 모듈 조합

```
FastAPI + LLM(Ollama/EXAONE) + DYNAMIC-PROMPT + lunar_python + STYLE-DARK
```

## 아키텍처

```
[브라우저] ←HTML→ [FastAPI :8888] ←HTTP→ [Ollama :11434]
                        │
                        ├── lunar_python (만세력 계산)
                        ├── pattern_engine (격국 판별, 16규칙)
                        ├── yongshin (용신/희기신 판별)
                        └── ten_gods (십신 계산)
```

단일 파일(`dashboard.py`)에 FastAPI 백엔드 + HTML 템플릿 내장.

## 특수 기능

| 기능 | 설명 |
|------|------|
| 만세력 계산 | `lunar_python` — 양력→음력→팔자 변환, 대운/세운 자동 계산 |
| 격국 판별 엔진 | 자평진전 16규칙 순차 적용 (주기투출, 잡기다용, 합거 등) |
| 신강/신약 판정 | 오행 기운 점수 기반 일간 강약 판정 |
| 용신/희기신 | 격국→용신→희신/기신/구신/한신 자동 판별 |
| 12운성 | 일간 기준 4지지 12운성 룩업 (양간 순행, 음간 역행) |
| 도화살 | 일지 기준 도화살 지지 판정 + 원국 내 유무 |
| 십신분포 | 8자 기준 비겁/식상/재성/관성/인성 5카테고리 집계 |
| 배우자궁 분석 | 일지 지장간 본기 십신 = 배우자성 |
| 세운 그리드 | 대운 클릭→해당 10년 세운 토글, 용신/기신 오행 색상 강조 |
| AI 9탭 해석 | 종합/성격/직업운/대운/재물운/배우자운/연애운/건강운/세운풀이 |
| 구체적 프롬프트 | "~할 수 있습니다" 금지, 단정형 풀이 유도 (직종/수입/결혼시기 등) |
| 툴팁 시스템 | 십신/오행 용어에 마우스 호버 시 설명 표시 |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| **FastAPI** | 비동기 웹 서버 (analyze + interpret 2개 엔드포인트) |
| **lunar_python** | 한국/중국 음양력 변환, 팔자/대운/세운 계산 (`Solar`, `Lunar`, `EightChar`, `Yun`, `DaYun`, `LiuNian`) |
| **Ollama (EXAONE 3.5)** | 로컬 LLM으로 사주 해석 생성 (7.8B 파라미터) |
| **httpx** | Ollama API 비동기 호출 |
| **Noto Serif KR** | 한자+한글 세리프 폰트 (사주 한자 표시) |
| **CSS Variables** | 다크 테마 + 오행별 색상 시스템 |

## API 엔드포인트

### POST /api/analyze
입력: `{ year, month, day, hour, minute, gender }`
출력:
```
pillars[]         사주 4주 (천간/지지/지장간/십신)
bazi_cn           한자 8글자
pattern           격국명 (정관격, 편재격 등)
body_strength     신강/신약/중화
yongshin          용신 (천간 + 십신 + 오행)
heeshin/gishin    희기신 4종
lucks[]           대운 8개 (각각 yearly[] 세운 10개 포함)
ten_god_summary   십신 5카테고리 분포
twelve_stages     12운성 (4지지)
peach_blossom     도화살 유무/위치
spouse_palace     배우자궁 십신
```

### POST /api/interpret
입력: analyze 결과 + category (9종)
출력: `{ text }` — LLM이 생성한 한국어 풀이

## 9개 해석 카테고리

| 카테고리 | 핵심 질문 |
|----------|-----------|
| 종합풀이 | 어떤 사람? 뭐하고 있나? 돈/결혼/인생 전환점 |
| 성격분석 | 겉과 속, 스트레스 반응, 연인에게 태도 |
| 직업운 | 구체적 직종 3개, 수입 수준, 사업vs직장 |
| 대운해석 | 시기별 취업/승진/결혼/건강 예측 |
| 재물운 | 부자 가능성, 수입 수준, 재테크 스타일 |
| 배우자운 | 결혼 시기, 배우자 성격/직업, 이혼/바람기 |
| 연애운 | 연애 횟수, 스타일, 모태솔로 가능성 |
| 건강운 | 약한 장기, 질환명, 관리법 |
| 세운풀이 | 향후 10년 연도별 좋은해/나쁜해 |

## 프롬프트 설계 핵심

모든 프롬프트에 공통 컨텍스트 주입:
```
【일간】, 【사주】, 【격국】, 【신강/신약】, 【용신】,
【희신/기신/구신/한신】, 【십신분포】, 【12운성】,
【도화살】, 【배우자궁】, 【성별】, 【대운】
```

핵심 지시: **"~할 수 있습니다" 같은 애매한 표현 금지. 단정적으로 쓸 것.**

## data 구조

```
(DB 없음, 모든 데이터 런타임 계산)
├── HIDDEN_STEMS_DATA    지장간 본기/중기/여기 (pattern_engine.py)
├── STAGE_START          12운성 시작 지지 (dashboard.py)
├── PEACH_BLOSSOM_MAP    도화살 룩업 (dashboard.py)
├── SAMHAP/SAMHOE        삼합/삼회 지지 조합 (pattern_engine.py)
└── TEN_GOD_LOOKUP       오행관계→십신 매핑 (ten_gods.py)
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 saju 레퍼런스를 보고
"[새 풀이 앱]"을 만들어줘.
FastAPI + LLM + DYNAMIC-PROMPT + lunar_python 조합.
다크 테마, 9개 카테고리 해석, 세운 그리드 포함.
프롬프트는 구체적 단정형으로 설계.
```
