# 기술 지도

> 어떤 기술이 어디에 쓰이는지 한눈에.
> 이 페이지 하나만 AI에게 던지면 됨.

---

## 기술 카테고리

### 🎨 프론트엔드

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **Tailwind CSS CDN** | 빌드 없이 유틸리티 CSS | salary, hexalounge |
| **Tailwind CSS v3 (빌드)** | Vite 빌드 방식 유틸리티 CSS | food |
| **CSS Variables** | `:root`로 테마 색상 관리 | pong, mz, tarot, dictionary |
| **Pretendard 폰트** | 한글 웹폰트 (CDN) | salary, mz, tok-wrapped |
| **Noto Sans KR** | Google Fonts 한글 웹폰트 | food, tarot |
| **시스템 폰트** | 로컬 폰트만 사용 | pong, amlife, dictionary, hexalounge |
| **Tailwind CSS v4 (@theme)** | PostCSS 빌드, @theme 커스텀 색상 | vibejob |
| **shadcn/ui (Radix UI)** | Headless 컴포넌트 (CVA + Tailwind) | vibejob |
| **Svelte 5** | 컴포넌트 기반 UI 프레임워크 | food, rackops |
| **D3.js** | 데이터 시각화 (Force Graph, 토폴로지) | rackops |
| **Lucide-Svelte** | Svelte 아이콘 팩 | rackops |
| **Lucide-React** | React 아이콘 팩 | vibejob |
| **React 18** | 컴포넌트 기반 UI 프레임워크 | tarot |
| **React 19** | 최신 React (App Router SSR/CSR) | vibejob |
| **Framer Motion** | React 애니메이션 라이브러리 | tarot |
| **Canvas API** | 레이더 차트 그리기 | mz, amlife, hexalounge, hexaconsulting |
| **html2canvas** | DOM → 이미지 캡처 | salary, pong, mz, amlife, hexaconsulting, tok-wrapped |
| **CSS 애니메이션** | fadeIn, slamIn, glitch, confetti, fadeUp, floatY | 전체 |
| **HTMX 2.0** | 서버 HTML 부분 교체 (hx-get/post/target/swap) | hexalounge, hexaconsulting |
| **Alpine.js** | 경량 프론트 반응성 (x-data, x-show) | hexalounge, hexaconsulting |

### 📡 API / SDK

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **Kakao JS SDK 2.7.4** | 카카오톡 공유 (sendDefault) | salary, pong, mz, amlife, hexaconsulting |
| **Kakao Local REST API** | 키워드 장소 검색 (반경 검색) | food |
| **Kakao scrapImage** | 공유 이미지 서버 업로드 | salary, pong, amlife |
| **Geolocation API** | GPS 현재 위치 | food |
| **Google Analytics 4** | 방문자/이벤트 트래킹 | salary, pong, mz, amlife |
| **Web Share API** | 모바일 네이티브 공유 | salary, pong, mz, amlife |
| **Clipboard API** | URL/텍스트 복사 | salary, pong, mz, amlife, hexaconsulting, tok-wrapped |
| **Web Worker** | 백그라운드 스레드 파일 파싱 | tok-wrapped |
| **PortOne (iamport)** | PG 결제 (카드/간편결제) | hexaconsulting |
| **Pillow (PIL)** | 서버사이드 이미지 생성 (동적 OG) | hexaconsulting |
| **Ollama** | 로컬 LLM (gemma3, exaone3.5 등) | tarot, psycho-bot, error-automation, human2, vibejob |
| **OpenAI API** | GPT-4o/4o-mini 직접 호출 | psycho-bot |
| **OpenRouter** | 클라우드 LLM API (gpt-4o-mini 등) | tarot |
| **sentence-transformers** | 로컬 임베딩 (E5-large 1024d, ko-sroberta 768d) | psycho-bot, human2 |
| **python-telegram-bot** | 텔레그램 봇 프레임워크 | psycho-bot, telbot, error-automation, human2 |
| **Twilio SDK** | 전화(TTS)/SMS 발송 | telbot, error-automation |
| **GitHub REST API** | repo 생성/관리 | git-uploader |
| **AWS S3 Presigned URLs** | 서버리스 파일 업로드 | vibejob |
| **Zod** | TypeScript 스키마 검증 | vibejob |
| **FastMCP** | Python MCP 서버 프레임워크 | wp-mcp |
| **WordPress REST API** | 글/카테고리/태그/미디어 CRUD | wp-mcp |
| **RankMath REST API** | SEO 메타 읽기/쓰기 | wp-mcp |
| **Pexels API** | 무료 스톡 이미지 검색 | wp-mcp |
| **Google Autocomplete** | 키워드 리서치 (API 키 불필요) | wp-mcp |
| **httpx** | Python 비동기 HTTP 클라이언트 | wp-mcp |
| **Web Audio API** | OscillatorNode 효과음 (외부 파일 불필요) | love |
| **Vibration API** | 모바일 햅틱 피드백 (graceful degradation) | love |
| **Touch Events** | 터치 스와이프 (touchstart/move/end) | love |

### 🖥️ 서버 / 인프라

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **AWS EC2** | 웹서버 호스팅 | 전체 |
| **Ubuntu + Nginx** | 정적 파일 서빙 | 전체 |
| **Cloudflare** | DNS + SSL + CDN | *.pearsoninsight.com |
| **GitHub Pages** | Docsify 문서 호스팅 | playbook |
| **Docker Compose** | 컨테이너 오케스트레이션 | tarot, psycho-bot |
| **FastAPI** | Python 비동기 REST API 서버 | tarot, psycho-bot, telbot, error-automation, rackops |
| **Django 6** | Python 풀스택 프레임워크 (ORM, Admin, Signal, Middleware) | hexalounge, hexaconsulting |
| **Gunicorn** | Python WSGI HTTP 서버 | hexaconsulting |
| **Apache (Reverse Proxy)** | 리버스 프록시 + 정적 파일 서빙 | hexaconsulting |
| **Go (net/http)** | Go 표준 라이브러리 HTTP 서버 | dictionary |
| **Redis** | 캐시 서버 (임베딩/RAG/대화기억/rate limit) | psycho-bot, human2, vibejob |
| **Alembic** | SQLAlchemy DB 마이그레이션 | psycho-bot |
| **PocketBase** | BaaS (DB+인증+파일+API) | collab-tool |
| **APScheduler** | 백그라운드 주기적 스케줄러 | rackops |
| **Paramiko** | SSH 클라이언트 (원격 명령어 실행) | rackops |
| **PySNMP** | SNMP 클라이언트 (iLO/IPMI 정보 수집) | rackops |
| **Next.js 15 (App Router)** | React 풀스택 프레임워크 (SSR/API Routes) | vibejob |
| **NextAuth.js 5** | 인증 프레임워크 (Credentials + Prisma Adapter) | vibejob |
| **SCP** | SSH 파일 전송 | 배포 파이프라인 |

### 🗄️ 데이터

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **JSON 파일** | 데이터 분리 (fetch) | salary, pong, amlife |
| **인라인 데이터** | JS 내 직접 임베딩 | mz |
| **URL 파라미터** | 결과 인코딩/디코딩 | mz, amlife |
| **PostgreSQL + pgvector** | 벡터 DB (임베딩 검색) | tarot, psycho-bot, human2 |
| **MySQL/MariaDB** | 관계형 DB (CRUD, 세션, 인증) | dictionary, rackops |
| **SQLite** | 파일 기반 경량 DB | error-automation, hexaconsulting |
| **pandas + openpyxl** | 엑셀 데이터 분석/가공 | product-j |
| **OpenPyXL** | 엑셀 비주얼 리포트 (셀 병합, 색상) | rackops |
| **Prisma ORM 6** | TypeScript ORM (스키마→마이그레이션→클라이언트) | vibejob |
| **PostgreSQL (Prisma)** | 관계형 DB (Prisma 통해 접근) | vibejob |
| **localStorage** | 히스토리 저장 (대시보드) | git-uploader, dictionary |

### 🎨 UI 프레임워크

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **Bootstrap 5** | UI 컴포넌트 프레임워크 | collab-tool |
| **Glassmorphism** | 블러+투명+네온 글래스 UI | collab-tool |
| **FullCalendar 6** | 캘린더 위젯 (월/주/리스트) | collab-tool |
| **Chart.js** | 차트 라이브러리 (Burn-up 등) | collab-tool |
| **Orbitron 폰트** | SF 스타일 제목 폰트 | collab-tool |

### 🛠️ 개발 도구

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **Vite 7** | 프론트엔드 빌드 + 개발 서버 + API 프록시 | food, rackops |
| **Flask (Python)** | 웹 프레임워크 (Blueprint) | git-uploader, collab-tool |
| **Git Credential Manager** | GitHub 토큰 자동 추출 | git-uploader |
| **Gradio** | Python ML 웹 UI (드래그&드롭+진행률) | whisper-script |
| **faster-whisper** | CTranslate2 Whisper 추론 (GPU fp16) | whisper-script |
| **imageio-ffmpeg** | FFmpeg 내장 바이너리 | whisper-script |
| **Docsify** | 마크다운 → 웹사이트 | playbook |

---

## 레퍼런스 × 기술 매트릭스

> ✅ = 사용함

| 기술 | salary | pong | mz | amlife | food | tarot | psycho-bot | telbot | collab-tool | product-j | error-auto | human2 | dictionary | rackops | hexalounge | hexaconsulting | tok-wrapped | vibejob | poli | whisper | wp-mcp | love | ideal |
|------|:------:|:----:|:--:|:------:|:----:|:-----:|:----------:|:------:|:-----------:|:---------:|:----------:|:------:|:----------:|:-------:|:----------:|:-------------:|:-----------:|:-------:|:----:|:-------:|:-------:|:----:|:-----:|
| **프론트엔드** | | | | | | | | | | | | | | | | | | | | | | |
| Tailwind CDN | ✅ | | | | | | | | | | | | | | ✅ | ✅ | | |  | | | |
| Tailwind v3 빌드 | | | | | ✅ | | | | | | | | | ✅ | | | | |  | | | |
| CSS Variables | | ✅ | ✅ | | | ✅ | | | ✅ | | | | ✅ | | | | | | ✅ | | ✅ | ✅ |
| Pretendard 폰트 | ✅ | | ✅ | | | | | | | | | | | | | | ✅ | | ✅ | ✅ | | ✅ | ✅ |
| Noto Sans KR | | | | | ✅ | ✅ | | | ✅ | | | | | | | | | |  | | | |
| Orbitron 폰트 | | | | | | | | | ✅ | | | | | | | | | |  | | | |
| HTMX 2.0 | | | | | | | | | | | | | | | ✅ | ✅ | | |  | | | |
| Alpine.js | | | | | | | | | | | | | | | ✅ | ✅ | | |  | | | |
| Svelte 5 | | | | | ✅ | | | | | | | | | ✅ | | | | |  | | | |
| D3.js | | | | | | | | | | | | | | ✅ | | | | |  | | | |
| Lucide-Svelte | | | | | | | | | | | | | | ✅ | | | | |  | | | |
| React 18 | | | | | | ✅ | | | | | | | | | | | | |  | | | |
| Framer Motion | | | | | | ✅ | | | | | | | | | | | | |  | | | |
| Bootstrap 5 | | | | | | | | | ✅ | | | | | | | | | |  | | | |
| Glassmorphism | | | | | | | | | ✅ | | | | | | | | | |  | | | |
| Vanilla JS SPA | | | | | | | | | | | | | ✅ | | | | | | ✅ | | ✅ | |
| Canvas 레이더차트 | | | ✅ | ✅ | | | | | | | | | | | ✅ | ✅ | | | ✅ | | ✅ | |
| html2canvas | ✅ | ✅ | ✅ | ✅ | | | | | | | | | | | | ✅ | ✅ | |  | | ✅ | ✅ |
| FullCalendar 6 | | | | | | | | | ✅ | | | | | | | | | |  | | | |
| Chart.js | | | | | | | | | ✅ | | | | | | | | | |  | | | |
| Tailwind CSS v4 (@theme) | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| React 19 | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| shadcn/ui (Radix UI) | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| Lucide-React | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| **API / SDK** | | | | | | | | | | | | | | | | | | | | | | |
| Kakao 공유 | ✅ | ✅ | ✅ | ✅ | | | | | | | | | | | | ✅ | | |  | | | |
| Kakao Local API | | | | | ✅ | | | | | | | | | | | | | |  | | | |
| Geolocation API | | | | | ✅ | | | | | | | | | | | | | |  | | | |
| Ollama (로컬 LLM) | | | | | | ✅ | ✅ | | | | ✅ | ✅ | | | | | | ✅ |  | | | |
| OpenAI API (직접) | | | | | | | ✅ | | | | | | | | | | | |  | | | |
| OpenRouter (클라우드 LLM) | | | | | | ✅ | | | | | | | | | | | | |  | | | |
| sentence-transformers | | | | | | | ✅ | | | | | ✅ | | | | | | |  | | | |
| python-telegram-bot | | | | | | | ✅ | ✅ | | | ✅ | ✅ | | | | | | |  | | | |
| Twilio (전화/SMS) | | | | | | | | ✅ | | | ✅ | | | | | | | |  | | | |
| Google Analytics | ✅ | ✅ | ✅ | ✅ | | | | | | | | | | | | | | |  | | | |
| Web Share API | ✅ | ✅ | ✅ | ✅ | | | | | | | | | | | | | | | ✅ | | ✅ | ✅ |
| PortOne (iamport) | | | | | | | | | | | | | | | | ✅ | | |  | | | |
| Pillow (PIL) | | | | | | | | | | | | | | | | ✅ | | | ✅ | | | ✅ |
| AWS S3 Presigned URLs | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| Zod (스키마 검증) | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| FastMCP (Python MCP) | | | | | | | | | | | | | | | | | | | | ✅ | | |
| WordPress REST API | | | | | | | | | | | | | | | | | | | | ✅ | | |
| RankMath REST API | | | | | | | | | | | | | | | | | | | | ✅ | | |
| Pexels API | | | | | | | | | | | | | | | | | | | | ✅ | | |
| Google Autocomplete | | | | | | | | | | | | | | | | | | | | ✅ | | |
| httpx (비동기 HTTP) | | | | | | | | | | | | | | | | | | | | ✅ | | |
| Clipboard API | ✅ | ✅ | ✅ | ✅ | | | | | | | | | | | | ✅ | ✅ | | | | ✅ | ✅ |
| Web Audio API (효과음) | | | | | | | | | | | | | | | | | | | | | ✅ | ✅ |
| Vibration API (햅틱) | | | | | | | | | | | | | | | | | | | | | ✅ | ✅ |
| Touch Events (스와이프) | | | | | | | | | | | | | | | | | | | | | ✅ | |
| **백엔드** | | | | | | | | | | | | | | | | | | | | | | |
| Django 6 | | | | | | | | | | | | | | | ✅ | ✅ | | |  | | | |
| FastAPI | | | | | | ✅ | ✅ | ✅ | | | ✅ | | | ✅ | | | | |  | | | |
| Flask (Blueprint) | | | | | | | | | ✅ | | | | | | | | | |  | | | |
| Go (net/http) | | | | | | | | | | | | | ✅ | | | | | |  | | | |
| PocketBase (BaaS) | | | | | | | | | ✅ | | | | | | | | | |  | | | |
| PostgreSQL + pgvector | | | | | | ✅ | ✅ | | | | | ✅ | | | | | | |  | | | |
| MySQL/MariaDB | | | | | | | | | | | | | ✅ | ✅ | | | | |  | | | |
| SQLite | | | | | | | | | | | ✅ | | | | ✅ | ✅ | | | ✅ | | | |
| Redis | | | | | | | ✅ | | | | | ✅ | | | | | | ✅ |  | | | |
| Django ORM | | | | | | | | | | | | | | | ✅ | ✅ | | |  | | | |
| Django Signals | | | | | | | | | | | | | | | ✅ | | | |  | | | |
| Django Admin | | | | | | | | | | | | | | | ✅ | ✅ | | |  | | | |
| Gunicorn | | | | | | | | | | | | | | | | ✅ | | |  | | | |
| Apache (Reverse Proxy) | | | | | | | | | | | | | | | | ✅ | | | ✅ | | | |
| APScheduler | | | | | | | | | | | | | | ✅ | | | | |  | | | |
| Paramiko (SSH) | | | | | | | | | | | | | | ✅ | | | | |  | | | |
| PySNMP (SNMP) | | | | | | | | | | | | | | ✅ | | | | |  | | | |
| OpenPyXL (엑셀 리포트) | | | | | | | | | | | | | | ✅ | | | | |  | | | |
| pandas + openpyxl | | | | | | | | | | ✅ | | | | | | | | |  | | | |
| Docker Compose | | | | | | ✅ | ✅ | | | | | | | | | | | |  | | | |
| RAG 파이프라인 | | | | | | ✅ | ✅ | | | | | ✅ | | | | | | |  | | | |
| SSE 스트리밍 | | | | | | ✅ | ✅ | | | | | | | | | | | |  | | | |
| Alembic (마이그레이션) | | | | | | | ✅ | | | | | | | | | | | |  | | | |
| SQLAlchemy 2.0 (async) | | | | | | ✅ | ✅ | | | | | | | | | | | |  | | | |
| bcrypt (세션 인증) | | | | | | | | | | | | | ✅ | | | | | ✅ |  | | | |
| Next.js 15 (App Router) | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| NextAuth.js 5 | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| Prisma ORM 6 | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| PostgreSQL (Prisma) | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| **앱 유형** | | | | | | | | | | | | | | | | | | | | | | |
| 계산기 (입력→계산) | ✅ | | | | | | | | | | | | | | | | | |  | | | |
| 데이터 분석 (엑셀) | | | | | | | | | | ✅ | | | | | | | | |  | | | |
| O/X 퀴즈 | | ✅ | | | | | | | | | | | | | | | | |  | | | |
| 선택형 퀴즈 | | | ✅ | ✅ | | | | | | | | | | | | | | | ✅ | | ✅ | |
| 추천기 (질문→검색) | | | | | ✅ | | | | | | | | | | | | | |  | | | |
| AI 상담 (LLM 대화) | | | | | | ✅ | ✅ | | | | | ✅ | | | | | | |  | | | |
| 텔레그램 봇 | | | | | | | ✅ | ✅ | | | ✅ | ✅ | | | | | | |  | | | |
| 알림 봇 (반복+확인) | | | | | | | | ✅ | | | ✅ | | | | | | | |  | | | |
| 업무 도구 (CRUD+KPI) | | | | | | | | | ✅ | | | | ✅ | ✅ | | | | |  | | | |
| DCIM 인프라 관리 | | | | | | | | | | | | | | ✅ | | | | |  | | | |
| SRE 장애 자동화 | | | | | | | | | | | ✅ | | | | | | | |  | | | |
| 페르소나 복제 챗봇 | | | | | | | | | | | | ✅ | | | | | | |  | | | |
| CLI 레퍼런스+실행기 | | | | | | | | | | | | | ✅ | | | | | |  | | | |
| 커뮤니티 플랫폼 (인증+매칭) | | | | | | | | | | | | | | | ✅ | | | |  | | | |
| 세일즈 퍼널 (진단→결제) | | | | | | | | | | | | | | | | ✅ | | |  | | | |
| 파일 분석기 (Wrapped) | | | | | | | | | | | | | | | | | ✅ | |  | | | |
| 프리랜서 매칭 플랫폼 | | | | | | | | | | | | | | | | | | ✅ | | | | |
| 스크립트 추출기 (음성→텍스트) | | | | | | | | | | | | | | | | | | | | ✅ | | | |
| MCP 서버 (개발 자동화) | | | | | | | | | | | | | | | | | | | | ✅ | | |
| 이상형 월드컵 (토너먼트) | | | | | | | | | | | | | | | | | | | | | | | ✅ |
| **특수 기능** | | | | | | | | | | | | | | | | | | | | | | | |
| 질문 타이머 (15초) | | ✅ | ✅ | ✅ | | | | | | | | | | | | | | | ✅ | | | ✅ | |
| 결과 공개 연출 | | ✅ | ✅ | ✅ | ✅ | ✅ | | | | | | | | | | | ✅ | | ✅ | | ✅ | ✅ |
| 콤보/상관관계 점수 | | ✅ | | | | | | | | | | | | | | | | |  | | | |
| 레이더 차트 | | | ✅ | ✅ | | | | | | | | | | | ✅ | ✅ | | | ✅ | | ✅ | |
| 결과 URL 공유 | | | ✅ | ✅ | | | | | | | | | | | | ✅ | | | ✅ | | ✅ | |
| LoL 티어 매핑 | ✅ | | | | | | | | | | | | | | | | | |  | | | |
| 성별 분기 | | ✅ | | ✅ | | | | | | | | | | | ✅ | | | |  | | | ✅ |
| 6각형 인증 시스템 | | | | | | | | | | | | | | | ✅ | | | |  | | | |
| 뱃지 기반 접근 제어 | | | | | | | | | | | | | | | ✅ | | | |  | | | |
| 3-Tier 매칭 (Mirror/Dream/Destiny) | | | | | | | | | | | | | | | ✅ | | | |  | | | |
| 인기도 Elo (Laplace smoothing) | | | | | | | | | | | | | | | ✅ | | | |  | | | |
| 양방향 좋아요 매칭 | | | | | | | | | | | | | | | ✅ | | | |  | | | |
| Admin 매칭 시뮬레이터 | | | | | | | | | | | | | | | ✅ | | | |  | | | |
| 포인트/월렛 시스템 | | | | | | | | | | | | | | | ✅ | | | |  | | | |
| Canvas 파티클 애니메이션 | | | | | | | | | | | | | | | ✅ | | | |  | | | |
| HTMX 부분 교체 | | | | | | | | | | | | | | | ✅ | ✅ | | |  | | | |
| JSON 폴링 채팅 | | | | | | | | | | | | | | | ✅ | | | |  | | | |
| 대댓글 (재귀 댓글) | | | | | | | | | | | | | | | ✅ | | | |  | | | |
| Toss 디자인 시스템 | | | | | | | | | | | | | | | ✅ | ✅ | | |  | | | |
| 수능 등급 매핑 (1~9) | | | | | | | | | | | | | | | | ✅ | | |  | | | |
| 불균형 감지 (gap ≥ 40) | | | | | | | | | | | | | | | | ✅ | | |  | | | |
| IP 기반 중복제거 카운팅 | | | | | | | | | | | | | | | | ✅ | | | ✅ | | | |
| Pillow 동적 OG 이미지 | | | | | | | | | | | | | | | | ✅ | | | ✅ | | | |
| PortOne PG 결제 | | | | | | | | | | | | | | | | ✅ | | |  | | | |
| FOMO 타이머+할인 | | | | | | | | | | | | | | | | ✅ | | |  | | | |
| GPS 위치 검색 | | | | | ✅ | | | | | | | | | | | | | |  | | | |
| 별점 필터/크롤링 | | | | | ✅ | | | | | | | | | | | | | |  | | | |
| 다시 뽑기 (거부 목록) | | | | | ✅ | | | | | | | | | | | | | |  | | | |
| Vite API 프록시 | | | | | ✅ | | | | | | | | | ✅ | | | | |  | | | |
| 3D 카드 뒤집기 | | | | | | ✅ | | | | | | | | | | | | |  | | | |
| 가드레일 (민감 주제) | | | | | | ✅ | | | | | | | | | | | | |  | | | |
| 대화형 채팅 | | | | | | ✅ | ✅ | | | | | ✅ | | | | | | |  | | | |
| 콜드 리딩 기법 | | | | | | ✅ | | | | | | | | | | | | |  | | | |
| 3단계 위기감지 | | | | | | | ✅ | | | | | | | | | | | |  | | | |
| 3단계 주제분류 | | | | | | | ✅ | | | | | | | | | | | |  | | | |
| 5모드 대화 | | | | | | | ✅ | | | | | | | | | | | |  | | | |
| 감정분류 | | | | | | | ✅ | | | | | | | | | | | |  | | | |
| 학습DB (자동개선) | | | | | | | ✅ | | | | | | | | | | | |  | | | |
| 자기인식 엔진 | | | | | | | ✅ | | | | | | | | | | | |  | | | |
| 그룹채팅 지원 | | | | | | | ✅ | | | | | | | | | | | |  | | | |
| 사용자 요청 감지 | | | | | | | ✅ | | | | | | | | | | | |  | | | |
| 반복 알림 (확인까지) | | | | | | | | ✅ | | | ✅ | | | | | | | |  | | | |
| Twilio 전화/SMS | | | | | | | | ✅ | | | ✅ | | | | | | | |  | | | |
| KPI 가중 평균 | | | | | | | | | ✅ | | | | | | | | | |  | | | |
| Burn-up 차트 | | | | | | | | | ✅ | | | | | | | | | |  | | | |
| FullCalendar 캘린더 | | | | | | | | | ✅ | | | | | | | | | |  | | | |
| Excel 내보내기 | | | | | | | | | ✅ | | | | | | | | | |  | | | |
| 다중 파일 업로드 | | | | | | | | | ✅ | | | | | | | | | |  | | | |
| 듀얼 테마 토글 | | | | | | | | | ✅ | | | | ✅ | | | | | |  | | | |
| JARVIS 배경 애니메이션 | | | | | | | | | ✅ | | | | | | | | | |  | | | |
| 엑셀 피벗 분석 | | | | | | | | | | ✅ | | | | | | | | |  | | | |
| 3단계 보고서 라이프사이클 | | | | | | | | | | | ✅ | | | | | | | |  | | | |
| 자연어 보고서 수정 | | | | | | | | | | | ✅ | | | | | | | |  | | | |
| 당직 관리 (Tier 에스컬레이션) | | | | | | | | | | | ✅ | | | | | | | |  | | | |
| 페르소나 7단계 프롬프트 | | | | | | | | | | | | ✅ | | | | | | |  | | | |
| 듀얼 메모리 (Redis+pgvector) | | | | | | | | | | | | ✅ | | | | | | |  | | | |
| 카톡 ETL (469만 메시지) | | | | | | | | | | | | ✅ | | | | | | |  | | | |
| 태도 기반 응답 모드 | | | | | | | | | | | | ✅ | | | | | | |  | | | |
| 청크 전송 (타이핑 효과) | | | | | | | | | | | | ✅ | | | | | | |  | | | |
| 변수 템플릿 시나리오 | | | | | | | | | | | | | ✅ | | | | | |  | | | |
| CLI 직접 실행 (exec) | | | | | | | | | | | | | ✅ | | | | | |  | | | |
| 레거시→신규 매핑 | | | | | | | | | | | | | ✅ | | | | | |  | | | |
| 공개/비공개 콘텐츠 | | | | | | | | | | | | | ✅ | | | | | |  | | | |
| 구문 하이라이팅 | | | | | | | | | | | | | ✅ | | | | | |  | | | |
| go:embed 단일 바이너리 | | | | | | | | | | | | | ✅ | | | | | |  | | | |
| 비주얼 랙 다이어그램 | | | | | | | | | | | | | | ✅ | | | | |  | | | |
| 네트워크 토폴로지 (D3.js) | | | | | | | | | | | | | | ✅ | | | | |  | | | |
| SSH/SNMP 자동 감지 | | | | | | | | | | | | | | ✅ | | | | |  | | | |
| SSH Console (웹 터미널) | | | | | | | | | | | | | | ✅ | | | | |  | | | |
| 비주얼 엑셀 리포트 | | | | | | | | | | | | | | ✅ | | | | |  | | | |
| 드래그&드롭 (랙 장비 이동) | | | | | | | | | | | | | | ✅ | | | | |  | | | |
| 카톡 .txt 파싱 (모바일+PC) | | | | | | | | | | | | | | | | | ✅ | |  | | | |
| Web Worker 파싱 | | | | | | | | | | | | | | | | | ✅ | |  | | | |
| 16캐릭터 룰기반 판정 | | | | | | | | | | | | | | | | | ✅ | |  | | | |
| MBTI 4축 추정 (4레이어) | | | | | | | | | | | | | | | | | ✅ | |  | | | |
| 대화 맥락 분석 (공감반응) | | | | | | | | | | | | | | | | | ✅ | |  | | | |
| 시간축 행동 패턴 분석 | | | | | | | | | | | | | | | | | ✅ | |  | | | |
| 한국어 언어 깊이 분석 | | | | | | | | | | | | | | | | | ✅ | |  | | | |
| 정밀 분석 리포트 (멤버별) | | | | | | | | | | | | | | | | | ✅ | |  | | | |
| 관계유형 추정 (8계층 REL-TYPE) | | | | | | | | | | | | | | | | | ✅ | |  | | | |
| Wrapped 카드 시퀀스 (13장) | | | | | | | | | | | | | | | | | ✅ | |  | | | |
| AI 견적 분석 (Ollama) | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| 에스크로 결제 | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| 개발자 등급 (7티어) | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| 마일스톤 관리 | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| 1:1 웹 채팅 | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| 스크롤 리빌 (4종) | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| RotatingText 히어로 | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| Rate Limiting (Redis) | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| 분쟁 처리 시스템 | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| Error Boundary (4영역) | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| Toast 알림 (Radix) | | | | | | | | | | | | | | | | | | ✅ |  | | | |
| 스와이프 답변 (Tinder식) | | | | | | | | | | | | | | | | | | | | | | ✅ | |
| 슬라이더 답변 (스펙트럼) | | | | | | | | | | | | | | | | | | | | | | ✅ | |
| 드래그 순위 답변 | | | | | | | | | | | | | | | | | | | | | | ✅ | |
| 혼합 질문 타입 (4종) | | | | | | | | | | | | | | | | | | | | | | ✅ | |
| **테마** | | | | | | | | | | | | | | | | | | | | | | |
| 라이트 | ✅ | | ✅ | ✅ | ✅ | | | | ✅ | | | | ✅ | | ✅ | ✅ | | ✅ | | ✅ | | | |
| 다크 | | ✅ | | | | ✅ | | | ✅ | | | | ✅ | ✅ | | | ✅ | | ✅ | | ✅ | ✅ |

---

## 레퍼런스 프로필 카드

### salary - 월급 계산기
```
유형: 계산기
URL:  salary.pearsoninsight.com
조합: BASE + DATA + CALC + GRADE + SHARE + GA + STYLE-LIGHT

입력 → 4대보험/소득세 계산 → 실수령액
     → 소득분위 상위 몇%
     → LoL 티어 매핑
     → 추천 차량/미국 비교

데이터: salary-data.json (세율, 세액표, 분위표, 티어, 차량)
폰트:   Pretendard
CSS:    Tailwind CDN
Kakao:  [프로젝트 소스 참조]
```

### pong - 퐁퐁 측정기
```
유형: O/X 자가진단
URL:  pong.pearsoninsight.com
조합: BASE + DATA + QUIZ + TIMER + GRADE + REVEAL + SHARE + GA + STYLE-DARK

36개 O/X → 가중점수 + 콤보 + 상관관계
        → 시그마~오메가 6등급
        → 성별 분기 (남/여 다른 질문셋)
        → 카테고리별 피드백

데이터: data.json (질문, 등급, 콤보, 상관관계)
폰트:   시스템 폰트
CSS:    순수 CSS + :root 변수 (다크)
특수:   킬러문항 강제등급, 패시브 보정
Kakao:  [프로젝트 소스 참조]
```

### mz - MZ력 측정기
```
유형: 선택형 다차원 테스트
URL:  mz.pearsoninsight.com
조합: BASE + QUIZ + TIMER + GRADE + RADAR + REVEAL + URL-ENCODE + SHARE + GA + STYLE-LIGHT

40문항 5지선다 → 8차원 점수
              → 레이더 차트
              → SSS~D 7등급
              → 세대별 비교

데이터: 인라인 (JS 내 직접)
폰트:   Pretendard
CSS:    순수 CSS + :root 변수 (라이트)
특수:   출생연도 입력, 세대 평균 비교, URL 결과공유
Kakao:  [프로젝트 소스 참조]
```

### amlife - 엠생력 측정기
```
유형: 선택형 다차원 테스트
URL:  amlife.pearsoninsight.com
조합: BASE + DATA + QUIZ + TIMER + GRADE + RADAR + REVEAL + URL-ENCODE + SHARE + GA + STYLE-LIGHT

60문항 4지선다 → 8차원 점수
              → 레이더 차트
              → S~F 6등급
              → 나이 가중치 보정

데이터: data.json (질문, 카테고리, 등급)
폰트:   시스템 폰트
CSS:    인라인 (라이트)
특수:   나이별 가중치, State machine 렌더링, URL 결과공유, 성별분기
Kakao:  [프로젝트 소스 참조]
```

### food - 오늘 뭐먹지?
```
유형: 추천기 (GPS 맛집 추천)
URL:  (로컬 개발 중)
스택: Svelte 5 + TypeScript + Vite 7 + Tailwind v3

3가지 질문 (기분, 음식종류, 시간여유)
  → 키워드 매핑 (mood×food×time → 검색어 3개)
  → GPS 위치 기반 반경 2km 식당 검색
  → 별점 필터 (3.5+/4.0+/4.5+)
  → 랜덤 추천 + 다시 뽑기

데이터: TypeScript 인라인 (keywordMap)
폰트:   Noto Sans KR (Google Fonts)
CSS:    Tailwind v3 빌드 (파스텔 그라데이션)
API:    Kakao Local REST API (Vite 프록시)
특수:   별점 크롤링, 거부 목록, confetti 연출
```

### tarot - 타로 마스터 루미나
```
유형: AI 타로 상담 (풀스택)
URL:  (로컬 개발 중)
스택: React 18 + FastAPI + PostgreSQL/pgvector + Ollama/OpenRouter

질문 입력 → 78장 중 카드 선택 (Fisher-Yates 셔플)
           → 3D 카드 뒤집기 공개
           → RAG 5개 소스 검색 → LLM 해석 생성
           → 대화형 채팅 (추가 질문 가능)

프론트: React 18, Framer Motion, React Router, Axios
백엔드: FastAPI, SQLAlchemy(async), pgvector, httpx
LLM:    Ollama(로컬) / OpenRouter(클라우드) 런타임 전환
RAG:    PKT원전 + 타로교안 + KB + 심리학 고전 + 상담기법
배포:   Docker Compose (PostgreSQL + Backend)
특수:   가드레일, 콜드리딩, 메모리매니저, QA매니저, SSE
```

### psycho-bot - AI 심리 상담 챗봇 (마음벗)
```
유형: AI 심리 상담 챗봇 (텔레그램/웹)
URL:  (개발 중)
조합: LLM + RAG + REDIS + DYNAMIC-PROMPT + TELEGRAM

백엔드: FastAPI + SQLAlchemy 2.0(async) + Alembic
DB:     PostgreSQL + pgvector (1024d) + Redis 7
LLM:    Ollama(exaone3.5:7.8b) / OpenAI(GPT-4o) / GGUF
임베딩: sentence-transformers (multilingual-e5-large 1024d)
봇:     python-telegram-bot 21 (개인/그룹)
배포:   Docker Compose (PostgreSQL + Redis)

NLP 파이프라인:
  위기감지(3단계) → 주제분류(3단계) → 모드감지(5모드) → 감정분류
  → RAG검색 + 대화요약 + 프로필 + 자기인식 → 프롬프트 조합 → LLM

특수:
  - 5가지 대화 모드 (상담/교육/친구/짧은답변/하이브리드)
  - 3단계 위기감지 (1393 자살예방 핫라인 연결)
  - 학습DB (대화에서 키워드/패턴 자동 추출)
  - 자기인식 엔진 (EXAONE-Deep 추론)
  - 사용자 요청 감지 ("반말해줘", "질문하지마" 등 JSONB)
  - 그룹채팅 + 관계 메타데이터
  - 18+ DB 테이블
```

### telbot - 텔레그램 트리거 알림 봇
```
유형: 알림 봇 (반복 알림 + 확인)
URL:  (내부 서비스)
조합: TELEGRAM + TWILIO + FastAPI

POST /trigger → 텔레그램 반복 알림 (🚨 [1], 🚨 [2], ...)
             → "✅ 확인" 버튼 누를 때까지 반복
             → Twilio 전화/SMS 에스컬레이션

백엔드: FastAPI + python-telegram-bot + Twilio SDK
상태:   인메모리 dict (alert_id → active)
특수:   UUID 알림 ID, 0.5~10초 간격, 다중 알림 동시
```

### collab-tool - 팀 협업 대시보드 (ARK-CORTEX)
```
유형: 업무 도구 (팀 협업 대시보드)
URL:  (내부 서비스)
조합: Flask + POCKETBASE + Bootstrap 5 + Chart.js + FullCalendar

5개 Blueprint:
  /tasks       → 태스크 CRUD + Excel 내보내기
  /calendar    → FullCalendar (우선순위 색상)
  /kpi         → 가중 KR + Burn-up 차트
  /completed   → 완료 아카이브
  /warehouse   → 지식 창고 + 다중 파일

백엔드: Flask + PocketBase (BaaS)
테마:   Glassmorphism 듀얼 (다크=JARVIS 네온 / 라이트=클린)
폰트:   Orbitron (제목) + Noto Sans KR (본문)
특수:   KPI 가중 평균, On-Track 분석, JARVIS 배경 애니메이션
```

### product-j - 엑셀 재고 분석기
```
유형: 데이터 분석 스크립트
URL:  (로컬 스크립트)
조합: Python + pandas + openpyxl

엑셀 재고 데이터 → 출고날짜 NULL 필터 (현재고)
                 → 위치별/제품별 집계
                 → 피벗 테이블 (제품×위치)
                 → 결과 엑셀 저장

데이터: inventory_sample.xlsx
특수:   NULL 기반 재고 판별, 피벗 테이블 자동 생성
```

### error-automation - SRE 장애 보고서 자동화 봇
```
유형: AI 챗봇 + 알림 봇 (SRE 장애 대응)
URL:  (내부 서비스)
조합: LLM + TELEGRAM + TWILIO + SQLite + FastAPI

장애 알림 → Ollama(gemma3:4b) 보고서 자동 생성
         → 3단계: 발생보고 → 경과보고 → 종료보고
         → 자연어 수정: "영향도를 VM 5대로 바꿔"
         → 에스컬레이션: 텔레그램 DM → 전화 → 다음 당직자

백엔드: FastAPI + python-telegram-bot + Twilio
DB:     SQLite (5개 테이블)
LLM:    Ollama (gemma3:4b)
특수:   3단계 보고서, 자연어 수정, 당직 Tier 에스컬레이션
```

### human2 - 고독한 나르시시스트 (페르소나 RAG 챗봇)
```
유형: AI 챗봇 (페르소나 복제)
URL:  (내부 서비스)
조합: LLM + RAG + REDIS + DYNAMIC-PROMPT + TELEGRAM

카톡 로그 469만 메시지 → ETL (파싱→청킹→추출→임베딩)
                       → 2,068 세션 벡터 DB 저장
                       → 7단계 동적 프롬프트 빌더
                       → 페르소나 재현 응답 생성

백엔드: python-telegram-bot 21 (폴링)
DB:     PostgreSQL + pgvector (768d) + Redis 7
LLM:    Ollama (exaone3.5:7.8b)
임베딩: ko-sroberta-multitask (768d, GPU)
특수:   듀얼 메모리, 태도 기반 응답, 카톡 ETL, 타이핑 효과
```

### dictionary - OpenStack CLI 위자드 V2
```
유형: 업무 도구 (CLI 사전 + 실행기 + 커뮤니티)
URL:  (로컬 서비스)
조합: Go (net/http) + MySQL + Vanilla JS SPA + CSS Variables

OpenStack 5모듈 + Linux 50+ 명령어 레퍼런스
  → 브라우저에서 CLI 직접 실행 (exec.Command)
  → 변수 템플릿 시나리오
  → 커뮤니티 공유 (팁/가이드/트러블슈팅)

백엔드: Go 1.21 (net/http, 프레임워크 없이)
DB:     MySQL (9개 테이블)
인증:   bcrypt + 쿠키 세션 (7일)
프론트: Vanilla JS SPA (index.html 단일 파일)
배포:   go:embed 단일 바이너리 (9.6MB)
특수:   CLI 실행, 변수 템플릿, 레거시→신규 매핑, 구문 하이라이팅
```

### rackops - DCIM 인프라 관리 시스템
```
유형: 업무 도구 (DCIM — 데이터센터 인프라 관리)
URL:  (내부 서비스)
조합: Svelte (Vite) + Tailwind CSS + D3.js + Lucide-Svelte
      + FastAPI + APScheduler + Paramiko (SSH) + PySNMP (SNMP) + OpenPyXL
      + MySQL

비주얼 랙 다이어그램 (42U/45U 가변 높이, 드래그&드롭, PDU)
  → SSH/SNMP 실시간 모니터링 (1분 폴링, 전력/온도/인터페이스)
  → Auto-Detect (IP/ID/PW → 모델명/시리얼 자동 수집)
  → 네트워크 토폴로지 (D3.js Force Graph, 줌/팬/드래그)
  → SSH Console (웹에서 명령어 실행)
  → 비주얼 엑셀 리포트 (셀 병합 + 색상, 위치/랙별 필터링)

프론트: Svelte (Vite), Tailwind CSS, D3.js, Lucide-Svelte
백엔드: FastAPI, Uvicorn, APScheduler, Paramiko, PySNMP, OpenPyXL
DB:     MySQL (locations, racks, physical_devices)
특수:   비주얼 랙, 네트워크 토폴로지, SSH/SNMP 모니터링, 엑셀 리포트
```

### hexalounge - 인증 기반 소셜 매칭 커뮤니티
```
유형: 커뮤니티 플랫폼 (인증+게시판+매칭+채팅+포인트)
GitHub: github.com/ganna40/hexalounge
조합: DJANGO + HTMX + Tailwind CDN + Alpine.js + Canvas RADAR + GRADE

6가지 인증 (연봉/외모/나이/직장/학벌/체형/MBTI)
  → Admin 심사 → 뱃지 자동 부여 (등급 세분화: 외모S/A/B, 자산Lv.1~3)
  → 뱃지 기반 게시판 접근 제어 (public/tier/gender/verified)
  → 3-Tier 매칭: Mirror(±5점) / Dream(+5~20점) / Destiny(MBTI궁합)
  → 인기도 Elo (Laplace smoothing) + spec 합산 점수
  → 양방향 좋아요 → 매칭 성사 → 72시간 1:1 채팅
  → 매칭 성사 Canvas 파티클 애니메이션

프론트: Tailwind CDN, HTMX 2.0, Alpine.js, Canvas (레이더+파티클)
백엔드: Django 6, Django ORM (SQLite), Signals, Middleware
앱:     accounts, verification, community, matching, chat, points
서비스: badge_service, board_access, matching_service, wallet_service
Admin:  매칭 시뮬레이터 (3-Tier 결과 + 대시보드 통계 8개)
디자인: Toss 디자인 시스템 (라이트)
특수:   3-Tier 매칭, Elo 인기도, 포인트 월렛, 고스트 모드, 보낸/받은 관심
```

### hexaconsulting - 연애 컨설팅 퍼널
```
유형: 세일즈 퍼널 (진단 → 결과 → 랜딩 → 결제)
URL:  hexaconsulting.pearsoninsight.com
GitHub: github.com/ganna40/hexaconsulting
조합: DJANGO + HTMX + Tailwind CDN + Alpine.js + RADAR + GRADE + PILLOW-OG + PORTONE + SHARE + DEPLOY

20문항 (Part A 하드웨어 5 + Part B 소프트웨어 15)
  → HTMX 파셜 스왑 (1문항씩 전환)
  → 6축 찌그러진 육각형 결과 + 수능 등급 (1~9)
  → Pillow OG 이미지 동적 생성 (800x800)
  → SNS 공유 (카카오톡/텔레그램/X/인스타) + html2canvas 캡처
  → 세일즈 랜딩 (문제제기→권위→상품→FOMO→FAQ)
  → PortOne 결제 + 서버 검증

프론트: Tailwind CDN, HTMX 2.0, Alpine.js, Canvas (레이더)
백엔드: Django 6, Gunicorn, Apache (reverse proxy)
앱:     diagnosis (테스트+결과+OG), consulting (랜딩+결제+주문)
DB:     SQLite (QuestionCategory, Question, Choice, DiagnosisSession, ConsultingProduct, ConsultingOrder)
특수:   수능 등급 매핑, 불균형 감지, IP 중복제거, Pillow OG, PortOne, FOMO 타이머
디자인: Toss 디자인 시스템 (라이트)
```

### tok-wrapped - 카카오톡 대화 Wrapped 분석기
```
유형: 파일 분석기 (Wrapped 스타일)
URL:  (GitHub Pages 배포 예정)
조합: BASE + SCREEN + GRADE + REVEAL + SHARE + CALC(숫자애니) + STYLE-DARK + WebWorker + MBTI추정엔진 + REL-TYPE

카카오톡 .txt 내보내기 파일 업로드
  → Web Worker로 메인 스레드 보호하며 파싱
  → 모바일+PC 포맷 정규식 파싱 (오전/오후→24시 변환)
  → 시간대/요일/단어/이모지/ㅋㅋ 등 통계 추출
  → 16캐릭터 룰기반 판정 (AI 없이)
  → MBTI 4축 추정 (사전+패턴+행동+심층 4레이어)
  → 대화 맥락 분석 (공감반응 T/F 킬러, 연속발송, 폭발메시지, 주도권)
  → 시간축 행동 패턴 (응답시간 분산, 요일 균일도, 에너지 기울기, 잠수→복귀)
  → 한국어 언어 깊이 (과거형/미래형, 완충어, 감정세밀도, 의성어/의태어)
  → 13장 Wrapped 카드 시퀀스 (그라데이션+카운트업+컨페티)
  → 정밀 분석 리포트 (멤버별 MBTI+레이더+역할+캐릭터)
  → html2canvas 이미지 저장 + 클립보드 복사

프론트: 순수 CSS (다크 Wrapped 테마, 그라데이션)
폰트:   Pretendard Variable (CDN)
특수:   MBTI 4레이어 추정, 공감반응 분석, 언어 깊이, 시간축 행동 패턴
서버:   없음 (100% 정적, 대화 데이터 브라우저 밖으로 안 나감)
```

### vibejob - 바이브잡 (프리랜서 매칭 플랫폼)
```
유형: 프리랜서 매칭 플랫폼 (프로젝트 등록→AI견적→제안→매칭→에스크로→리뷰)
URL:  (개발 중)
스택: Next.js 15 (App Router) + React 19 + Prisma 6 + NextAuth 5 + Tailwind v4 + shadcn/ui

의뢰자: 프로젝트 등록 → AI(Ollama) 카테고리/예산/일정 분석
      → 개발자 제안 수신 → 매칭 → 에스크로 결제 → 마일스톤 관리 → 검수 → 리뷰
개발자: 프로필(포트폴리오/스킬) → 프로젝트 탐색/제안
      → 7티어 등급(ROOKIE~GRANDMASTER, 수수료 40%→10%)
      → 정산(월렛) → 코드 리뷰/유지보수 카테고리
관리자: 유저/프로젝트/결제/분쟁/리뷰/카테고리/설정 대시보드

프론트: React 19, Tailwind CSS v4 (@theme 커스텀), shadcn/ui (Radix UI + CVA), Lucide-React
백엔드: Next.js 15 App Router (API Routes), NextAuth.js 5 (Credentials + Prisma Adapter)
DB:     PostgreSQL + Prisma ORM 6 + Redis (rate limiting)
AI:     Ollama (견적 분석, 코드 리뷰 견적)
파일:   AWS S3 Presigned URLs (이미지/파일 업로드)
검증:   Zod (스키마 검증)
보안:   Redis rate limiting, crypto.randomUUID, Error Boundary 4개
특수:   에스크로 결제, 7티어 등급, 마일스톤, 1:1채팅, 알림, 분쟁 처리
랜딩:   /about — RotatingText 히어로, 스크롤 리빌(4종), 등급바, AI견적 애니메이션, 마키
디자인: 라이트 테마 (커스텀 디자인 시스템)
속도:   서버→클라이언트 사이드 fetch 전환 (즉시 네비게이션)
```

---

### poli - 정치성향 테스트
```
유형: 정치성향 바이럴 테스트
URL:  https://poli.pearsoninsight.com
스택: Vanilla HTML/CSS/JS (단일 파일) + Pretendard 폰트 + Canvas 레이더차트

로직: 12문항 × 양방향 ls값 → score 누적 → leftPct(0~100%) → 7단계 성향
     axisScore(eco/sec/env/soc/val) / AXIS_MAX → 5축 레이더 차트 0~100% 정규화
     결과 인물: jm.webp(진보) / yu.jpg(중도) / tr.jpg(보수)

TIMER:    문항당 20초 카운트다운, force reflow 패턴(void bar.offsetWidth), 초과→자동 중립
URL-ENCODE: ?r=012... (val+1: -1,0,1→0,1,2), 공유 링크로 결과 즉시 복원
CALC:     통계 숫자 cubic ease-out requestAnimationFrame 카운트업
OG:       Pillow 1200×630 동적 이미지, ?v=1 캐시버스팅

카운터:   Python http.server + SQLite, CF-Connecting-IP → SHA256 해시, INSERT OR IGNORE
서버:     Apache2 VirtualHost + Let's Encrypt + Cloudflare(Flexible SSL)
         ProxyPass /visit /count → 127.0.0.1:8002 (systemd poli-counter.service)
삽질:    Cloudflare Flexible + certbot --redirect = ERR_TOO_MANY_REDIRECTS
         해결: poli.conf에서 RewriteRule 제거 (HTTP→HTTPS는 Cloudflare에 맡김)
디자인:  다크 테마 (블루↔레드 그라데이션), Pretendard Variable
```

### whisper-script - 동영상 자막 추출기
```
유형: 스크립트 추출기 (동영상 → 자막/텍스트)
URL:  http://127.0.0.1:7860 (로컬 전용)
스택: Python + Gradio + faster-whisper (CTranslate2) + CUDA fp16 + imageio-ffmpeg

로직: 동영상 드래그&드롭 → FFmpeg 오디오 추출 → Whisper large-v3 추론 → SRT/VTT/TXT 출력
     _clean/ 폴더에 필러 제거 + 중복 제거된 AI 요약용 텍스트 자동 생성

배치 처리: 여러 동영상 동시 업로드, 순차 처리 + 큐/진행률 표시
다중 포맷: TXT (순수 텍스트) + SRT (자막) + VTT (웹 자막)
모델 선택: tiny ~ large-v3 (5단계, 품질 vs 속도)
다국어:   한국어/영어/일본어/중국어/자동감지

AI 전처리: clean_text() / clean_srt() — 필러(음,어,네,그쵸 등) + SRT 포맷 + 중복 제거
          원본 대비 토큰 ~65% 절감 → Haiku 모델 사용 시 비용 ~3.5%

삽질:    FFmpeg PATH 충돌 → imageio-ffmpeg 내장 바이너리로 해결 (별도 설치 불필요)
         large-v3 첫 실행 시 ~3GB 다운로드 (이후 캐싱)
         GPU OOM 시 medium 모델로 변경 (품질 약간↓, 속도 2배↑)
디자인:  라이트 테마 (Toss 스타일), Pretendard Variable (CDN)
```

### wp-mcp - WordPress SEO MCP 서버
```
유형: MCP 서버 (개발 자동화 도구)
GitHub: github.com/ganna40/wp-generation-mcp
로컬:  C:\Users\ganna\Downloads\wp-generation-mcp
스택:  Python + FastMCP + httpx + WordPress REST API + RankMath API + Pexels API

Claude Code에서 블로그 글 작성 → SEO 최적화 → 스타일 체크 → 예약 발행 자동화
  18개 MCP 도구:
    wp_check_connection    — 연결 + 인증 + RankMath 확인
    wp_keyword_research    — Google 자동완성 키워드 리서치
    wp_check_cannibalization — 기존 글 키워드 중복 체크
    wp_create_post         — 글 생성 (SEO 메타 자동 설정, 슬러그 자동)
    wp_update_post         — 글 수정
    wp_list_posts          — 글 목록
    wp_get_post            — 글 상세 조회
    wp_list_drafts         — 초안/예약 글 목록
    wp_seo_check           — SEO 분석 + 구체적 수정 제안 (실패 항목별 액션)
    wp_find_image          — Pexels/Unsplash/Pixabay 이미지 검색 + WP 업로드
    wp_upload_media        — URL → WP 미디어 업로드
    wp_find_internal_links — 3단계 유사도 매칭 내부 링크 추천
    wp_review_draft        — 초안 종합 리뷰 (서버사이드 SEO 점수)
    wp_schedule_draft      — 예약 발행 (ISO 8601)
    wp_publish_pipeline    — 이미지→글생성→리뷰 통합 파이프라인
    wp_seo_optimize        — 기존 글 SEO 자동 최적화
    wp_extract_style_dna   — 스타일 DNA 추출 (프로필+가이드+few-shot 샘플)
    wp_style_check         — AI 문체 패턴 감지 (문단/1인칭/구어체/여담)

파이프라인:
  키워드 리서치 → 카니발리제이션 체크
    → 스타일 DNA 추출 (기존 글 분석 → 스타일 가이드 + few-shot)
    → 글 작성 (스타일 가이드 주입) + 이미지 검색/업로드
    → 글 생성 (draft) + RankMath SEO 메타 설정
    → SEO 체크 (수정 제안 포함) + 스타일 체크 (AI 패턴 감지)
    → 서버사이드 SEO 점수 계산 (PHP endpoint)
    → 종합 리뷰 → 사용자 확인 후 예약 발행

WordPress 필수: RankMath SEO + Code Snippets (SEO + posts-keywords endpoint)
특수: SEO 수정 제안, 3단계 내부링크 매칭, 스타일 DNA+few-shot, AI 문체 감지
```

### love - 나의 연애 유형 테스트
```
유형: 연애 유형 바이럴 테스트 (혼합 질문 타입)
URL:  love.pearsoninsight.com
스택: Vanilla HTML/CSS/JS (단일 파일) + Pretendard 폰트 + Canvas 레이더차트

로직: 15문항 혼합 (SWIPE 5 + SPECTRUM 4 + RANK 1 + CHOICE 5)
     → 5축 점수 (rom/ind/adv/stb/emo) 누적
     → 우세 축 기반 결과 판정 (5유형)
     → Canvas 레이더차트 5축 0~100% 정규화

새 모듈 (6개):
  SWIPE — Touch Events Tinder식 좌우 스와이프 답변 (threshold 100px, rotation 0.08)
  SPECTRUM — input[range] 슬라이더, leftScores↔rightScores 보간 답변
  DRAG-RANK — 터치/마우스 드래그 순위 매기기, 가중치 곱셈 (1위×4, 2위×3 ...)
  CAPTURE — html2canvas DOM→PNG, 결과 이미지 캡처/저장
  SOUND — Web Audio API OscillatorNode 효과음 (tick/swipeR/swipeL/reveal 아르페지오)
  HAPTIC — Vibration API 진동 피드백 (tap 30ms / select 50ms / result 팡파르)

기존 모듈: TIMER + RADAR + URL-ENCODE + SHARE + CALC + REVEAL

디자인: 다크 테마 (핑크↔보라 그라데이션), Pretendard Variable
특수: 혼합 질문 타입 (4종), 음소거 버튼, 결과 이미지 캡처, CSS 그라데이션+이모지 디자인
```

### ideal - 이상형 월드컵
```
유형: 이상형 월드컵 (토너먼트)
URL:  ideal.pearsoninsight.com
조합: BASE + SCREEN + TOURNAMENT + CAPTURE + SOUND + HAPTIC + SHARE + OG + STYLE-DARK

64명 셀럽 → Fisher-Yates 셔플 → 64강→32강→...→결승
           → 이미지 프리로딩 (64장 로드 후 게임 시작)
           → VS 카드 대결 + PICK 스탬프 + confetti 우승 연출
           → html2canvas 결과 캡처 + Web Share + 링크 복사
           → 성별 분기 (남자용=여자셀럽64 / 여자용=남자셀럽64)

데이터: 인라인 (JS 파이프 구분 문자열, W_RAW/M_RAW)
이미지: img/f/1~64.jpg + img/m/1~64.jpg
폰트:   Pretendard Variable (CDN)
CSS:    순수 CSS + :root 변수 (다크)
OG:     Pillow gen_og.py (1200x630 정적 이미지)
특수:   토너먼트 엔진, 이미지 프리로딩, 효과음(Web Audio), 햅틱
```

---

## AI에게 줄 때

이 페이지를 복사해서 프롬프트에 붙이고:

```
위 기술지도를 참고해서 "___" 앱을 만들어줘.

타입: [pong처럼 O/X | mz처럼 선택형 | salary처럼 계산기 | food처럼 추천기 | tarot/human2처럼 AI챗봇 | error-automation처럼 SRE봇 | telbot처럼 알림봇 | collab-tool/dictionary처럼 업무도구 | rackops처럼 DCIM | hexalounge처럼 커뮤니티 | hexaconsulting처럼 세일즈퍼널 | tok-wrapped처럼 파일분석기 | vibejob처럼 매칭플랫폼 | poli처럼 정치성향테스트 | whisper-script처럼 스크립트추출기 | wp-mcp처럼 MCP서버 | ideal처럼 이상형월드컵]
테마: [다크 | 라이트]
필요 모듈: [QUIZ + TIMER + GRADE + RADAR + REVEAL + SHARE + ...]
참고 레퍼런스: [pong | mz | amlife | salary | food | tarot | psycho-bot | telbot | collab-tool | product-j | error-automation | human2 | dictionary | rackops | hexaconsulting | tok-wrapped | vibejob | poli | whisper-script | wp-mcp | love | ideal]

추가 요구:
- ...
```

이것만 던지면 AI가 전체 구조를 이해하고 바로 만들 수 있음.
