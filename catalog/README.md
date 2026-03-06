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
| [PORTONE](catalog/portone.md) | PG 결제 (PortOne/아임포트) | 서버 (Django/Flask) |
| [PILLOW-OG](catalog/pillow-og.md) | 서버사이드 OG 이미지 동적 생성 | 서버 + Pillow |
| [REL-TYPE](catalog/rel-type.md) | 관계 유형 추정 (8계층 신호) | 없음 |
| [SWIPE](catalog/swipe.md) | 스와이프 답변 (Tinder식 좌/우) | BASE |
| [SPECTRUM](catalog/spectrum.md) | 슬라이더 답변 (0~100 스펙트럼) | BASE |
| [DRAG-RANK](catalog/drag-rank.md) | 드래그 순위 매기기 | BASE |
| [CAPTURE](catalog/capture.md) | 결과 이미지 캡처 (html2canvas) | 없음 |
| [SOUND](catalog/sound.md) | 효과음 (Web Audio API) | 없음 |
| [HAPTIC](catalog/haptic.md) | 햅틱 피드백 (Vibration API) | 없음 |
| [TOURNAMENT](catalog/tournament.md) | 토너먼트 월드컵 엔진 (N강 대결) | BASE, SCREEN |
| [REACT-FLOW](catalog/react-flow.md) | 노드 기반 다이어그램 캔버스 (@xyflow/react) | React |
| [DND-KIT](catalog/dnd-kit.md) | 드래그 앤 드롭 툴킷 (@dnd-kit/core) | React |
| [PLAYWRIGHT-SCRAPE](catalog/playwright-scrape.md) | Playwright Stealth 크롤링 (SPA/iframe/봇탐지우회) | 없음 |
| [DEPLOY](catalog/deploy.md) | EC2 배포 파이프라인 | 없음 |
| [JSPDF](catalog/jspdf.md) | PDF 생성 (jsPDF + html2canvas) | 없음 |
| [PWA](catalog/pwa.md) | 프로그레시브 웹 앱 (SW + manifest) | 없음 |
| [VIEW-TRANSITIONS](catalog/view-transitions.md) | View Transitions API 화면 전환 | 없음 |
| [CONFETTI](catalog/confetti.md) | 축하 컨페티 효과 (canvas-confetti) | 없음 |
| [LOTTIE](catalog/lottie.md) | 벡터 애니메이션 (lottie-web) | 없음 |

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

### "세일즈 퍼널" (hexaconsulting 같은)
```
DJANGO + HTMX + Tailwind CDN + Alpine.js + RADAR + GRADE + PILLOW-OG + PORTONE + SHARE + DEPLOY
```

### "혼합 질문 타입 테스트" (love 같은)
```
BASE + DATA + SCREEN + QUIZ + SWIPE + SPECTRUM + DRAG-RANK + TIMER + GRADE + RADAR + REVEAL + CAPTURE + SOUND + HAPTIC + URL-ENCODE + SHARE + GA + STYLE-DARK
```

### "이상형 월드컵" (ideal 같은)
```
BASE + SCREEN + TOURNAMENT + CAPTURE + SOUND + HAPTIC + SHARE + OG + STYLE-DARK
```

### "인프라 견적서 빌더" (infra-quote 같은)
```
REACT-FLOW + DND-KIT + React 19 + Vite + Tailwind CSS v4 + Lucide-React + Express (JSON DB)
```

### "사주 AI 풀이 대시보드" (saju 같은)
```
FastAPI + LLM(Ollama) + DYNAMIC-PROMPT + lunar_python + CSS Variables (다크)
```

### "파일 분석기 Wrapped" (tok-wrapped 같은)
```
BASE + SCREEN + GRADE + REVEAL + SHARE + CALC(숫자애니) + STYLE-DARK + WebWorker + MBTI추정엔진 + REL-TYPE
```

### "퇴직금 계산기 + PWA" (quit-calculator 같은)
```
BASE + CALC + GRADE + SHARE + CAPTURE + JSPDF + PWA + VIEW-TRANSITIONS + CONFETTI + LOTTIE + STYLE-LIGHT
```
