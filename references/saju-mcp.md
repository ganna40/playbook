# saju-mcp - 사주팔자 MCP 서버

> GitHub: https://github.com/ganna40/saju-mcp
> 로컬: C:\Users\ganna\saju-mcp

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | MCP 서버 (AI 사주 상담 도구) |
| **한줄 설명** | Claude Code에서 만세력 계산→격국 분석→교차 분석→과거 역추적→서사 생성→전문 상담까지 올인원 |
| **타겟** | 사주 상담 자동화, AI 명리학 연구자 |
| **스택** | Python + FastMCP 3.0 + Pydantic v2 + lunar_python |

## 모듈 조합

```
FastMCP + lunar_python + 28개 core 모듈 + knowledge DB
```

## 아키텍처

```
[Claude Code / MCP Client]
        │
        ▼
[FastMCP Server (server.py)]
        │
        ├── 만세력 계산 ──── lunar_python (음양력 변환, 4주 산출)
        │
        ├── 기본 분석 엔진
        │   ├── manseryeok.py      만세력 (4주 + 지장간 + 대운)
        │   ├── ten_gods.py        십신 계산
        │   ├── pattern_engine.py  격국 판별 (16규칙)
        │   ├── yongshin.py        용신/희기신 판별
        │   ├── strength.py        신강/신약 (0~100)
        │   ├── interactions.py    합충형파해
        │   └── sinsal.py          12종 신살 + 대운 발동
        │
        ├── 전문 분석 엔진
        │   ├── wealth.py          재물그릇 v2 (9항목 100점)
        │   ├── radar.py           6축 운세 레이더
        │   ├── life_events.py     인생이벤트 타임라인
        │   ├── yearly_events.py   연도별 사건 예측
        │   ├── twelve_stages.py   십이운성 계산/해석
        │   ├── naeum.py           납음오행 (60갑자)
        │   ├── gongmang.py        공망 (空亡)
        │   ├── johu.py            조후 용신
        │   └── palace.py          궁위 해석
        │
        ├── 고도화 엔진 (Expert Engine)
        │   ├── cross_analysis.py    교차 분석 (11개 패턴 탐지)
        │   ├── retrodiction.py      과거 역추적 (복음/반음 감지)
        │   ├── narrative_engine.py   종합 서사 생성
        │   ├── deep_consult.py      질문 기반 전문 상담
        │   └── interpretation.py    종합 해석 힌트
        │
        ├── 보고서/내보내기
        │   ├── report.py            성패 관점 종합 보고서
        │   ├── export.py            JSON/마크다운 내보내기
        │   ├── export_pdf.py        PDF 보고서
        │   └── compatibility.py     궁합 분석
        │
        └── knowledge/              지식 DB (인덱서/서처)
```

## 11개 MCP 도구

| 도구 | 용도 |
|------|------|
| `saju_analyze` | 종합 분석 (만세력→격국→십신→합충→신살→재물→레이더→교차→역추적→서사) |
| `saju_report` | 성패 관점 종합 보고서 (마크다운) |
| `saju_yearly` | 연도별 세운 분석 |
| `saju_compatibility` | 두 사람 궁합 분석 |
| `saju_sinsal` | 신살 상세 분석 |
| `saju_wealth` | 재물그릇 상세 분석 |
| `saju_life_events` | 인생 이벤트 타임라인 |
| `saju_export` | JSON/마크다운 내보내기 |
| `saju_export_pdf` | PDF 보고서 생성 |
| `saju_consult` | 질문 기반 전문 상담 (10개 카테고리) |
| `saju_knowledge_context` | 지식 DB 검색 |

## Expert Engine (고도화 엔진)

### 교차 분석 (cross_analysis.py) — 11개 패턴 탐지

| 패턴 | 감지 조건 |
|------|-----------|
| 식상생재 | 식신/상관 + 정재/편재 동시 존재 |
| 관인상생 | 정관/편관 + 정인/편인 동시 존재 |
| 상관견관 | 상관 + 정관 충돌 |
| 편인도식 | 편인 + 식신 억압 |
| 비겁쟁재 | 비견/겁재 과다 + 재성 존재 |
| 살인상생 | 편관(살) + 인성 상생 |
| 재관쌍미 | 재성 + 관성 균형 |
| 신강/약×격국 긴장 | 신강도와 격국 불일치 |
| 합충×궁위 | 합충이 궁위(년/월/일/시)에 미치는 영향 |
| 신살 클러스터 | 신살 3개 이상 집중 |
| 대운 흐름 | 현재 대운의 복음/반음/용신 관계 |

### 과거 역추적 (retrodiction.py)

대운 전환점마다 과거 사건을 예측:
- 복음(伏吟) 감지 — 대운 지지 = 일지
- 반음(反吟) 감지 — 대운 지지 ↔ 일지 충
- 대운 천간/지지의 십신 변화 기반 사건 추론
- 질문 hook 생성 ("이 시기에 ~한 일이 있었나요?")

### 종합 서사 (narrative_engine.py)

| 항목 | 설명 |
|------|------|
| one_line | 한 줄 정의 ("산 같은 무토, ~") |
| personality_story | 성격 서사 |
| life_arc | 인생 흐름 (대운 기반) |
| current_chapter | 현재 시점 해석 |
| top3_insights | 핵심 인사이트 3개 |
| practical_advice | 실용 조언 리스트 |

### 전문 상담 (deep_consult.py)

10개 상담 카테고리:
```
career_change  이직/전직    career    직업적성
business       사업운       wealth    재물운
love           연애운       marriage  결혼운
health         건강운       yearly    올해운세
study          학업적성     general   일반상담
```

## 핵심 데이터 모델 (models.py)

```python
SajuAnalysisResult
├── pillars            4주 (천간/지지/지장간/십신)
├── strength           신강/신약 (점수, 판정)
├── pattern            격국 (이름, 설명)
├── yongshin           용신/희기신
├── ten_gods           십신 분포
├── interactions       합충형파해
├── sinsal             신살 리스트
├── wealth             재물그릇 (등급/점수/규모)
├── radar              6축 레이더
├── daeun              대운 8개 (세운 포함)
├── life_events        인생이벤트
├── cross_insights     교차 분석 인사이트 (Expert)
├── retrodictions      과거 역추적 (Expert)
└── narrative          종합 서사 (Expert)
```

## saju-app과의 차이

| 항목 | saju-app (대시보드) | saju-mcp (MCP 서버) |
|------|---------------------|---------------------|
| 인터페이스 | FastAPI + 브라우저 | MCP (Claude Code 내장) |
| LLM 의존 | EXAONE 필수 (풀이 생성) | 불필요 (Claude가 직접 해석) |
| 해석 방식 | 규칙 초안 → LLM 다듬기 | 규칙 데이터 → Claude 직접 풀이 |
| 고도화 엔진 | 없음 | 교차분석/역추적/서사/전문상담 |
| 상담 | 카테고리 선택 후 일방향 | 대화형 (질문→답→꼬리질문) |

## MCP 설정

```bash
claude mcp add saju-mcp -- python "C:\Users\ganna\saju-mcp\server.py"
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 saju-mcp 레퍼런스를 보고
"[새 MCP 서버]"를 만들어줘.
FastMCP + Pydantic v2 + 도메인 전문 분석 엔진 조합.
교차 분석(패턴 탐지) + 과거 역추적 + 서사 생성 + 전문 상담 구조.
saju-mcp의 Expert Engine 아키텍처를 참고해서 만들어.
```
