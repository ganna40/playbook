# 기술 지도

> 어떤 기술이 어디에 쓰이는지 한눈에.
> 이 페이지 하나만 AI에게 던지면 됨.

---

## 기술 카테고리

### 🎨 프론트엔드

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **Tailwind CSS CDN** | 빌드 없이 유틸리티 CSS | salary |
| **Tailwind CSS v3 (빌드)** | Vite 빌드 방식 유틸리티 CSS | food |
| **CSS Variables** | `:root`로 테마 색상 관리 | pong, mz, tarot |
| **Pretendard 폰트** | 한글 웹폰트 (CDN) | salary, mz |
| **Noto Sans KR** | Google Fonts 한글 웹폰트 | food, tarot |
| **시스템 폰트** | 로컬 폰트만 사용 | pong, amlife |
| **Svelte 5** | 컴포넌트 기반 UI 프레임워크 | food |
| **React 18** | 컴포넌트 기반 UI 프레임워크 | tarot |
| **Framer Motion** | React 애니메이션 라이브러리 | tarot |
| **Canvas API** | 레이더 차트 그리기 | mz, amlife |
| **html2canvas** | DOM → 이미지 캡처 | salary, pong, mz, amlife |
| **CSS 애니메이션** | fadeIn, slamIn, glitch, confetti | 전체 |

### 📡 API / SDK

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **Kakao JS SDK 2.7.4** | 카카오톡 공유 (sendDefault) | salary, pong, mz, amlife |
| **Kakao Local REST API** | 키워드 장소 검색 (반경 검색) | food |
| **Kakao scrapImage** | 공유 이미지 서버 업로드 | salary, pong, amlife |
| **Geolocation API** | GPS 현재 위치 | food |
| **Google Analytics 4** | 방문자/이벤트 트래킹 | salary, pong, mz, amlife |
| **Web Share API** | 모바일 네이티브 공유 | salary, pong, mz, amlife |
| **Clipboard API** | URL/텍스트 복사 | salary, pong, mz, amlife |
| **Ollama** | 로컬 LLM (gemma3, exaone3.5 등) | tarot, psycho-bot |
| **OpenAI API** | GPT-4o/4o-mini 직접 호출 | psycho-bot |
| **OpenRouter** | 클라우드 LLM API (gpt-4o-mini 등) | tarot |
| **sentence-transformers** | 로컬 임베딩 (E5-large 1024d) | psycho-bot |
| **python-telegram-bot** | 텔레그램 봇 프레임워크 | psycho-bot |
| **GitHub REST API** | repo 생성/관리 | git-uploader |

### 🖥️ 서버 / 인프라

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **AWS EC2** | 웹서버 호스팅 | 전체 |
| **Ubuntu + Nginx** | 정적 파일 서빙 | 전체 |
| **Cloudflare** | DNS + SSL + CDN | *.pearsoninsight.com |
| **GitHub Pages** | Docsify 문서 호스팅 | playbook |
| **Docker Compose** | 컨테이너 오케스트레이션 | tarot, psycho-bot |
| **FastAPI** | Python 비동기 REST API 서버 | tarot, psycho-bot |
| **Redis** | 캐시 서버 (임베딩/RAG/프로필) | psycho-bot |
| **Alembic** | SQLAlchemy DB 마이그레이션 | psycho-bot |
| **SCP** | SSH 파일 전송 | 배포 파이프라인 |

### 🗄️ 데이터

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **JSON 파일** | 데이터 분리 (fetch) | salary, pong, amlife |
| **인라인 데이터** | JS 내 직접 임베딩 | mz |
| **URL 파라미터** | 결과 인코딩/디코딩 | mz, amlife |
| **PostgreSQL + pgvector** | 벡터 DB (임베딩 검색) | tarot, psycho-bot |
| **localStorage** | 히스토리 저장 (대시보드) | git-uploader |

### 🛠️ 개발 도구

| 기술 | 설명 | 사용처 |
|------|------|--------|
| **Vite 7** | 프론트엔드 빌드 + 개발 서버 + API 프록시 | food |
| **Flask (Python)** | 로컬 대시보드 서버 | git-uploader |
| **Git Credential Manager** | GitHub 토큰 자동 추출 | git-uploader |
| **Docsify** | 마크다운 → 웹사이트 | playbook |

---

## 레퍼런스 × 기술 매트릭스

> ✅ = 사용함

| 기술 | salary | pong | mz | amlife | food | tarot | psycho-bot |
|------|:------:|:----:|:--:|:------:|:----:|:-----:|:----------:|
| **프론트엔드** | | | | | | | |
| Tailwind CDN | ✅ | | | | | | |
| Tailwind v3 빌드 | | | | | ✅ | | |
| CSS Variables | | ✅ | ✅ | | | ✅ | |
| Pretendard 폰트 | ✅ | | ✅ | | | | |
| Noto Sans KR | | | | | ✅ | ✅ | |
| Svelte 5 | | | | | ✅ | | |
| React 18 | | | | | | ✅ | |
| Framer Motion | | | | | | ✅ | |
| Canvas 레이더차트 | | | ✅ | ✅ | | | |
| html2canvas | ✅ | ✅ | ✅ | ✅ | | | |
| **API / SDK** | | | | | | | |
| Kakao 공유 | ✅ | ✅ | ✅ | ✅ | | | |
| Kakao Local API | | | | | ✅ | | |
| Geolocation API | | | | | ✅ | | |
| Ollama (로컬 LLM) | | | | | | ✅ | ✅ |
| OpenAI API (직접) | | | | | | | ✅ |
| OpenRouter (클라우드 LLM) | | | | | | ✅ | |
| sentence-transformers | | | | | | | ✅ |
| python-telegram-bot | | | | | | | ✅ |
| Google Analytics | ✅ | ✅ | ✅ | ✅ | | | |
| Web Share API | ✅ | ✅ | ✅ | ✅ | | | |
| **백엔드** | | | | | | | |
| FastAPI | | | | | | ✅ | ✅ |
| PostgreSQL + pgvector | | | | | | ✅ | ✅ |
| Redis | | | | | | | ✅ |
| Docker Compose | | | | | | ✅ | ✅ |
| RAG 파이프라인 | | | | | | ✅ | ✅ |
| SSE 스트리밍 | | | | | | ✅ | ✅ |
| Alembic (마이그레이션) | | | | | | | ✅ |
| SQLAlchemy 2.0 (async) | | | | | | ✅ | ✅ |
| **앱 유형** | | | | | | | |
| 계산기 (입력→계산) | ✅ | | | | | | |
| O/X 퀴즈 | | ✅ | | | | | |
| 선택형 퀴즈 | | | ✅ | ✅ | | | |
| 추천기 (질문→검색) | | | | | ✅ | | |
| AI 상담 (LLM 대화) | | | | | | ✅ | ✅ |
| 텔레그램 봇 | | | | | | | ✅ |
| **특수 기능** | | | | | | | |
| 질문 타이머 (15초) | | ✅ | ✅ | ✅ | | | |
| 결과 공개 연출 | | ✅ | ✅ | ✅ | ✅ | ✅ | |
| 콤보/상관관계 점수 | | ✅ | | | | | |
| 레이더 차트 | | | ✅ | ✅ | | | |
| 결과 URL 공유 | | | ✅ | ✅ | | | |
| LoL 티어 매핑 | ✅ | | | | | | |
| 성별 분기 | | ✅ | | ✅ | | | |
| GPS 위치 검색 | | | | | ✅ | | |
| 별점 필터/크롤링 | | | | | ✅ | | |
| 다시 뽑기 (거부 목록) | | | | | ✅ | | |
| Vite API 프록시 | | | | | ✅ | | |
| 3D 카드 뒤집기 | | | | | | ✅ | |
| 가드레일 (민감 주제) | | | | | | ✅ | |
| 대화형 채팅 | | | | | | ✅ | ✅ |
| 콜드 리딩 기법 | | | | | | ✅ | |
| 3단계 위기감지 | | | | | | | ✅ |
| 3단계 주제분류 | | | | | | | ✅ |
| 5모드 대화 | | | | | | | ✅ |
| 감정분류 | | | | | | | ✅ |
| 학습DB (자동개선) | | | | | | | ✅ |
| 자기인식 엔진 | | | | | | | ✅ |
| 그룹채팅 지원 | | | | | | | ✅ |
| 사용자 요청 감지 | | | | | | | ✅ |
| **테마** | | | | | | | |
| 라이트 | ✅ | | ✅ | ✅ | ✅ | | |
| 다크 | | ✅ | | | | ✅ | |

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
조합: LLM + RAG + TELEGRAM

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

---

## AI에게 줄 때

이 페이지를 복사해서 프롬프트에 붙이고:

```
위 기술지도를 참고해서 "___" 앱을 만들어줘.

타입: [pong처럼 O/X | mz처럼 선택형 | salary처럼 계산기 | food처럼 추천기 | tarot처럼 AI상담 | psycho-bot처럼 AI챗봇]
테마: [다크 | 라이트]
필요 모듈: [QUIZ + TIMER + GRADE + RADAR + REVEAL + SHARE + ...]
참고 레퍼런스: [pong | mz | amlife | salary | food | tarot | psycho-bot]

추가 요구:
- ...
```

이것만 던지면 AI가 전체 구조를 이해하고 바로 만들 수 있음.
