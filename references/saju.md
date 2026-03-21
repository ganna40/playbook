# saju - 사주팔자 AI 프리미엄 상담 서비스

> GitHub: https://github.com/ganna40/saju_app_20260319
> 소스: C:\Users\ganna\saju_app_20260318
> URL: http://localhost:8000 (무료) / http://localhost:8000/premium (프리미엄)

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | AI 사주 상담 + 프리미엄 퍼널 서비스 (saju-mcp→분석엔진→Claude Opus 4.6 해석) |
| **한줄 설명** | 무료 스토리텔링 사주 → 소액 리포트(재물/연애/진로) → CEO급 프리미엄 전략 → AI 멘토 구독 |
| **타겟** | 일반인(무료) → 직장인/자산가(프리미엄) |
| **테마** | 무료: 다크 (인디고 악센트) / 프리미엄: 다크 (골드 악센트, 세리프 폰트) |
| **LLM** | Claude Opus 4.6 (claude -p subprocess 호출) |

## 수익 퍼널 구조

```
유입 (Free)          →  맛보기 스토리텔링 사주 + 공유하기(바이럴)
전환 (9,900원)       →  재물운/연애결혼/진로학업 상세 리포트
핵심수익 (39,900원)  →  CEO급 인생 전략 대시보드 (Executive Summary + 5년 액션플랜)
리텐션 (19,900원/월) →  AI 사주 멘토 챗봇 구독
```

## 프리미엄 티어별 리포트 구조

### Essential (9,900원) - 3종

**재물운 상세 리포트** (`PREMIUM_WEALTH_PROMPT`)
- 올해 재물운 등급 (S~D) + 분기별 흐름 + 자산 포트폴리오 + 리스크 경고

**연애/결혼 완전 분석** (`PREMIUM_LOVE_PROMPT`)
- 연애 DNA 진단 + 배우자 프로필(일지·배우자성 기반) + 5년 타이밍 + 부부 관계 전망

**진로/학업 완전 분석** (`PREMIUM_CAREER_PROMPT`)
- 학습 DNA 진단 + 최적 진로 TOP 3(십성·격국 기반) + 시험운 타이밍 + 커리어 로드맵

### Premium VIP (39,900원) (`PREMIUM_SYSTEM_PROMPT`)

```
1. Executive Summary (핵심 전략 요약)
   - 현재 인생 페이즈 / 핵심 성공 무기 / 최대 리스크
2. Wealth & Asset Strategy (맞춤형 자산 증식 솔루션)
   - 자산 축적 형태 / 투자 주의점 / 재물운 폭발 시기
3. Career & Business Roadmap (직업 및 커리어 전략)
   - 최적 포지셔닝 / 업무 스타일 / 3년 커리어 지침
4. Timing & Action Plan (5년 행동 지침)
   - 2026~2030 세운 기반 해야 할 일 / 피해야 할 일
5. VVIP Secret Note (컨설턴트의 당부)
```

### 프리미엄 프롬프트 원칙
- 추상적 비유 금지 → 구체적 타이밍 + 행동 지침
- 모든 조언에 명리학적 근거 괄호 병기 (예: "편관 대운 때문")
- 리스크 매니지먼트 필수 포함

## 모듈 조합

```
FastAPI + saju-mcp(core 직접 import) + Claude Opus 4.6(subprocess) + SSE Streaming
```

## 아키텍처

```
[브라우저 SPA]
  ├── /              index.html (무료 채팅 + 공유 + 업셀 배너)
  └── /premium       premium.html (티어 선택 → 폼 → 분석 → 후속질문)
        ↓
[FastAPI :8000]
  ├── POST /api/chat      (무료 분석 + 후속질문)
  └── POST /api/premium   (티어별 프리미엄 분석)
        │
        ├── saju-mcp core 모듈 직접 import (20+ 분석 함수)
        │   ├── manseryeok     만세력 계산 (사주 4주)
        │   ├── ten_gods       십신 계산
        │   ├── strength       신강/신약 정밀 계산
        │   ├── pattern_engine 격국 판별
        │   ├── yongshin       용신/희기신 판별
        │   ├── sinsal         신살 판별 + 대운 발동
        │   ├── interactions   합충형파해 분석
        │   ├── wealth         재물그릇 분석
        │   ├── life_events    인생이벤트 타임라인
        │   ├── radar          6축 운세 레이더
        │   ├── twelve_stages  12운성
        │   ├── palace         궁위 분석
        │   ├── cross_analysis 교차 패턴 분석
        │   ├── retrodiction   과거 역추적
        │   ├── narrative      서사 생성
        │   └── deep_consult   후속질문 심층 상담
        │
        ├── TIER_CONFIG 매핑 (티어→프롬프트+데이터추출 자동 선택)
        │   ├── wealth  → PREMIUM_WEALTH_PROMPT  + extract_wealth_data()
        │   ├── love    → PREMIUM_LOVE_PROMPT    + extract_love_data()
        │   ├── career  → PREMIUM_CAREER_PROMPT  + extract_career_data()
        │   └── premium → PREMIUM_SYSTEM_PROMPT  + extract_premium_data()
        │
        └── claude -p --model claude-opus-4-6 (subprocess, 300초 타임아웃)
              → SSE 청크 스트리밍 (8자 단위)
```

## 프롬프트 크기 최적화

티어별 필요한 데이터만 추출하여 프롬프트 크기 최소화:

| 함수 | 추출 데이터 | 용도 |
|------|------------|------|
| `extract_wealth_data()` | pillars, strength, pattern, yongshin, wealth, daeun, interactions, ten_gods | 재물운 |
| `extract_love_data()` | pillars, ten_gods, sinsal, interactions, daeun, palace, life_events, cross_insights | 연애/결혼 |
| `extract_career_data()` | pillars, ten_gods, strength, pattern, yongshin, sinsal, daeun, life_events, cross_insights | 진로/학업 |
| `extract_premium_data()` | 위 전체 + wealth + narrative (retrodictions, palace 등 제외) | 프리미엄 VIP |

## 프론트엔드 구조

### index.html (무료 채팅)
- 바닐라 JS SPA, SSE 스트리밍, 마크다운 렌더링
- 분석 완료 후: 공유하기 버튼 (Web Share API / 클립보드) + 프리미엄 업셀 카드

### premium.html (프리미엄 랜딩 + 분석)
- 골드 테마 (세리프 폰트, 금색 그라데이션)
- 6개 티어 카드 랜딩 → 생년월일시 폼 → SSE 스트리밍 결과
- 무료 분석 후 업셀 배너 (재물운/연애/진로/프리미엄)
- 후속 질문 채팅 기능 (deep_consult 엔진 연동)

## data 구조

```
saju_app_20260318/
├── main.py                          FastAPI 서버 (전체 라우팅 + 분석 로직)
├── requirements.txt                 의존성
├── static/
│   ├── index.html                   무료 채팅 SPA
│   └── premium.html                 프리미엄 랜딩 + 분석 SPA
├── app/
│   ├── prompts/
│   │   ├── saju_system.py           무료 시스템 프롬프트 (스토리텔링형)
│   │   └── saju_premium.py          프리미엄 프롬프트 4종 (VIP/재물/연애/진로)
│   ├── api/routes/saju.py           (레거시 API 라우트)
│   ├── core/config.py               설정
│   ├── db/session.py                PostgreSQL async 세션
│   ├── models/saju_cache.py         캐시 모델
│   ├── schemas/saju.py              Pydantic 스키마
│   └── services/
│       ├── saju_interpreter.py      Anthropic API 직접 호출 서비스
│       └── saju_prompt_builder.py   프롬프트 빌더
└── tests/
    └── test_saju_interpreter.py
```

## 외부 의존

| 의존 | 역할 |
|------|------|
| **saju-mcp** (`C:\Users\ganna\saju-mcp`) | 사주 분석 코어 엔진 (20+ 모듈, sys.path 직접 import) |
| **Claude CLI** (`claude -p`) | LLM 해석 (Opus 4.6, subprocess 호출) |

## AI에게 비슷한 거 만들게 하려면

```
playbook의 saju 레퍼런스를 보고
"[새 사주 상담 앱]"을 만들어줘.
FastAPI + saju-mcp(core import) + Claude subprocess + SSE 스트리밍 조합.
프리미엄 퍼널: 무료(스토리텔링) → Essential(9,900원, 재물/연애/진로) → VIP(39,900원, CEO급 전략).
골드 테마 프리미엄 랜딩, 티어별 프롬프트/데이터추출 최적화.
모든 조언에 명리학적 근거 병기, 구체적 타이밍+행동 지침 위주.
```
