# 모듈 카탈로그

> 레고 블록처럼 조합해서 앱을 만드는 빌딩블록.
> 각 모듈은 독립적이며, 필요한 것만 골라서 조합.

## 한눈에 보기

| 모듈 | 용도 | 의존성 |
|------|------|--------|
| [BASE](catalog/base.md) | SPA 기본 골격 (HTML + 모바일) | 없음 |
| [DATA](catalog/data.md) | JSON 데이터 분리 패턴 | 없음 |
| [SCREEN](catalog/screen.md) | 화면 전환 (인트로→진행→결과) | BASE |
| [QUIZ](catalog/quiz.md) | 퀴즈/설문 엔진 | BASE, DATA, SCREEN |
| [CALC](catalog/calc.md) | 계산기 엔진 | BASE, DATA, SCREEN |
| [GRADE](catalog/grade.md) | 등급/티어 시스템 | DATA |
| [RADAR](catalog/radar.md) | 레이더 차트 (Canvas) | 없음 |
| [KAKAO](catalog/kakao.md) | 카카오톡 공유 | 없음 |
| [KAKAO-LOCAL](catalog/kakao-local.md) | 카카오 로컬 API (장소 검색) | 없음 |
| [OG](catalog/og.md) | Open Graph 메타태그 | 없음 |
| [SHARE](catalog/share.md) | 통합 공유 (카카오+URL+스크린샷) | KAKAO, OG |
| [GA](catalog/ga.md) | Google Analytics 트래킹 | 없음 |
| [TIMER](catalog/timer.md) | 질문별 타이머 (15초) | QUIZ |
| [REVEAL](catalog/reveal.md) | 결과 공개 연출 (슬램/글리치/컨페티) | GRADE |
| [URL-ENCODE](catalog/url-encode.md) | 결과를 URL로 공유 | 없음 |
| [STYLE-DARK](catalog/style-dark.md) | 다크 테마 CSS | BASE |
| [STYLE-LIGHT](catalog/style-light.md) | 라이트 테마 CSS | BASE |
| [LLM](catalog/llm.md) | LLM 연동 (Ollama/OpenAI/OpenRouter/GGUF) | 없음 |
| [RAG](catalog/rag.md) | RAG 파이프라인 (벡터 검색) | LLM |
| [TELEGRAM](catalog/telegram.md) | 텔레그램 봇 (python-telegram-bot) | 없음 |
| [TWILIO](catalog/twilio.md) | 전화/SMS 알림 (Twilio) | 없음 |
| [POCKETBASE](catalog/pocketbase.md) | BaaS (DB+인증+파일+API) | 없음 |
| [REDIS](catalog/redis.md) | 캐시 + 세션 + 대화 기억 | 없음 |
| [DYNAMIC-PROMPT](catalog/dynamic-prompt.md) | 동적 프롬프트 빌더 (변수 주입) | LLM |
| [DJANGO](catalog/django.md) | Django 풀스택 프레임워크 | 없음 |
| [HTMX](catalog/htmx.md) | 서버 렌더링 인터랙션 | 서버 (Django/Flask) |
| [DEPLOY](catalog/deploy.md) | EC2 배포 파이프라인 | 없음 |

## 조합 예시

### "바이럴 O/X 테스트" (퐁퐁 같은)
```
BASE + DATA + SCREEN + QUIZ + TIMER + GRADE + REVEAL + SHARE + GA + STYLE-DARK
```

### "계산기" (월급계산기 같은)
```
BASE + DATA + SCREEN + CALC + GRADE + SHARE + GA + STYLE-LIGHT
```

### "다차원 분석" (MZ력, 엠생력 같은)
```
BASE + DATA + SCREEN + QUIZ + TIMER + GRADE + RADAR + REVEAL + URL-ENCODE + SHARE + GA + STYLE-LIGHT
```

### "GPS 맛집 추천기" (food 같은)
```
KAKAO-LOCAL + Svelte/React + Vite + Tailwind
```

### "AI 상담 풀스택" (tarot 같은)
```
LLM + RAG + DYNAMIC-PROMPT + React + FastAPI + PostgreSQL/pgvector + Docker
```

### "AI 챗봇 (텔레그램)" (psycho-bot 같은)
```
LLM + RAG + REDIS + DYNAMIC-PROMPT + TELEGRAM + FastAPI + PostgreSQL/pgvector + Docker
```

### "알림 봇" (telbot 같은)
```
TELEGRAM + TWILIO + FastAPI
```

### "페르소나 RAG 챗봇" (human2 같은)
```
LLM + RAG + REDIS + DYNAMIC-PROMPT + TELEGRAM + PostgreSQL/pgvector
```

### "업무 도구 대시보드" (collab-tool 같은)
```
Flask + POCKETBASE + Bootstrap 5 + Chart.js + FullCalendar
```

### "DCIM 인프라 관리" (rackops 같은)
```
Svelte + Tailwind CSS + D3.js + FastAPI + APScheduler + Paramiko + PySNMP + OpenPyXL + MySQL
```

### "커뮤니티 플랫폼" (hexalounge 같은)
```
DJANGO + HTMX + Tailwind CDN + Alpine.js + Canvas RADAR + GRADE
```
