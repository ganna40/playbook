# 조립 가이드

> 만들고 싶은 앱 타입을 골라 → 부품을 조립하면 끝.
> 로봇 조립하듯이: **뼈대 + 두뇌 + 얼굴 + 입출력 + 기억장치**

---

## 앱 타입 9종

| 타입 | 뭘 만드는 건지 | 대표 작품 | 난이도 |
|------|---------------|-----------|--------|
| **바이럴 테스트** | 사람들이 공유하는 성격/능력 테스트 | pong, mz, amlife | ★☆☆ |
| **계산기** | 입력하면 결과 나오는 도구 | salary | ★☆☆ |
| **추천기** | 질문 → 외부 API 검색 → 추천 | food | ★★☆ |
| **AI 챗봇** | AI가 대화하는 서비스 | tarot, psycho-bot | ★★★ |
| **알림 봇** | 자동 알림/경고 시스템 | telbot | ★★☆ |
| **업무 도구** | 팀 협업 대시보드 | collab-tool | ★★★ |
| **커뮤니티 플랫폼** | 인증+게시판+매칭+채팅 | hexalounge | ★★★ |
| **세일즈 퍼널** | 진단→결과→랜딩→결제 | hexaconsulting | ★★☆ |
| **파일 분석기** | 파일 업로드→브라우저 파싱→Wrapped 카드 | tok-wrapped | ★☆☆ |

---

## 부품 카테고리

```
모든 앱 = 뼈대 + 두뇌 + 얼굴 + 입출력 + 기억장치

뼈대(Skeleton) : 앱의 기본 구조. HTML, 프레임워크, 화면 전환
두뇌(Brain)    : 핵심 로직. 퀴즈 엔진, 계산기, LLM, 검색
얼굴(Face)     : 보이는 것. 테마, 차트, 애니메이션, 결과 연출
입출력(I/O)    : 바깥 세상과 연결. 공유, 알림, GPS, 분석
기억(Memory)   : 데이터 저장. JSON, DB, 캐시
```

---

## 타입 1: 바이럴 테스트

> "10문항 풀면 너의 ○○력은?" → 결과 카드 → 카톡 공유 → 바이럴

```
뼈대: BASE + SCREEN
두뇌: QUIZ + GRADE
얼굴: STYLE-DARK 또는 STYLE-LIGHT + REVEAL
입출력: SHARE(KAKAO+OG) + GA
기억: DATA (JSON)
```

**옵션 부품:**

| 원하는 기능 | 부품 추가 |
|------------|----------|
| 15초 타이머 | + TIMER |
| 레이더 차트 | + RADAR |
| URL로 결과 공유 | + URL-ENCODE |
| 콤보/상관관계 보너스 | 직접 구현 (pong 참고) |
| 세대별 비교 | 직접 구현 (mz 참고) |

**참고 레퍼런스:** [pong](references/pong.md) (O/X), [mz](references/mz.md) (선택형), [amlife](references/amlife.md) (선택형+나이)

---

## 타입 2: 계산기

> "월급 입력하면 실수령액 + 세금 + 등급 나오는 도구"

```
뼈대: BASE + SCREEN
두뇌: CALC + GRADE
얼굴: STYLE-LIGHT
입출력: SHARE(KAKAO+OG) + GA
기억: DATA (JSON — 세율표, 등급표 등)
```

**참고 레퍼런스:** [salary](references/salary.md), [product-j](references/product-j.md) (엑셀 데이터 분석)

---

## 타입 3: 추천기

> "질문 3개 → GPS + API 검색 → 맞춤 추천"

```
뼈대: Svelte 또는 React + Vite + Tailwind
두뇌: KAKAO-LOCAL (장소 검색) + 키워드 매핑 로직
얼굴: Tailwind CSS + confetti 연출
입출력: Geolocation API (GPS)
기억: TypeScript 인라인 데이터
```

**참고 레퍼런스:** [food](references/food.md)

---

## 타입 4: AI 챗봇

> "AI가 사용자와 대화. RAG로 지식 검색, LLM으로 답변 생성"

```
뼈대: FastAPI (백엔드) + React 또는 TELEGRAM (프론트)
두뇌: LLM + RAG + DYNAMIC-PROMPT
얼굴: (프론트 선택에 따라) React UI / 텔레그램 채팅
입출력: SSE 스트리밍 + TELEGRAM 또는 웹
기억: PostgreSQL + pgvector + REDIS
```

**규모별 선택:**

| 규모 | LLM | 임베딩 | 프론트 |
|------|-----|--------|--------|
| 가벼운 | Ollama (gemma3:4b) | nomic-embed-text (768d) | 텔레그램 봇 |
| 본격적 | Ollama (exaone3.5:7.8b) + OpenAI 백업 | E5-large (1024d) | React + SSE |
| 멀티플랫폼 | 듀얼 프로바이더 | sentence-transformers | 텔레그램+디스코드+웹 |

**참고 레퍼런스:** [tarot](references/tarot.md) (웹 AI상담), [psycho-bot](references/psycho-bot.md) (텔레그램 AI상담), [human2](references/human2.md) (페르소나 복제), [error-automation](references/error-automation.md) (SRE 보고서 자동화)

---

## 타입 5: 알림 봇

> "이벤트 발생 → 텔레그램/SMS/전화로 반복 알림 → 확인 누를 때까지"

```
뼈대: FastAPI
두뇌: 이벤트 감지 + 반복 알림 로직
얼굴: (없음 — 봇이 UI)
입출력: TELEGRAM + TWILIO (전화/SMS)
기억: 인메모리 (dict)
```

**참고 레퍼런스:** [telbot](references/telbot.md) (단순 반복 알림), [error-automation](references/error-automation.md) (SRE 에스컬레이션)

---

## 타입 6: 업무 도구

> "팀 태스크 관리 + KPI 추적 + 캘린더 + 지식창고"

```
뼈대: Flask + Jinja2 템플릿
두뇌: CRUD + KPI 가중평균 계산 + 검색/필터
얼굴: Bootstrap 5 + Glassmorphism + Chart.js + FullCalendar
입출력: Excel 내보내기 + 파일 업로드
기억: POCKETBASE (BaaS)
```

**참고 레퍼런스:** [collab-tool](references/collab-tool.md) (Flask+PocketBase), [dictionary](references/dictionary.md) (Go+MySQL CLI 위자드), [rackops](references/rackops.md) (Svelte+FastAPI DCIM)

---

## 타입 7: 커뮤니티 플랫폼

> "인증으로 신뢰도 쌓고, 게시판에서 소통하고, 매칭으로 만나는 서비스"

```
뼈대: DJANGO (ORM, Admin, Template, Signal, Middleware)
두뇌: 인증 심사 + 매칭 알고리즘 + 접근 제어
얼굴: Tailwind CDN + HTMX (부분 교체) + Canvas RADAR
입출력: HTMX (좋아요/댓글/무한스크롤) + JSON 폴링 (채팅)
기억: SQLite (개발) → PostgreSQL (프로덕션)
```

**핵심 패턴:**

| 패턴 | 설명 |
|------|------|
| 뱃지 시스템 | 서류 업로드 → Admin 심사 → 자동 뱃지 부여 (Signal) |
| 접근 제어 | 게시판별 조건 (티어/성별/인증) → Service 레이어 분리 |
| 3-Tier 매칭 | Mirror(안정감) / Dream(상향) / Destiny(운명) 3명 추천 |
| 인기도 Elo | Laplace smoothing `(좋아요+1)/(좋아요+패스+2)` |
| UserInteraction | LIKE/PASS/MATCH 모든 상호작용 추적 → 인기도 실시간 갱신 |
| Admin 시뮬레이터 | get_urls() 오버라이드 → 커스텀 뷰에서 매칭 결과 시뮬레이션 |
| 포인트 월렛 | 충전/소비 트랜잭션 + 잔액 관리 (Service 레이어 분리) |
| HTMX 부분 교체 | full page vs partial 분기 (`HX-Request` 헤더 감지) |
| JSON 폴링 채팅 | 2초 간격 fetch → 새 메시지 append → bubble 애니메이션 |
| Canvas 파티클 | 매칭 성사 시 하트/별/원 버스트 애니메이션 |

**참고 레퍼런스:** [hexalounge](references/hexalounge.md) (Django+HTMX 인증 매칭 커뮤니티)

---

## 타입 8: 세일즈 퍼널

> "바이럴 진단 → 찌그러진 육각형 결과 → 전문가 랜딩 → PG 결제"

```
뼈대: DJANGO (ORM, Admin, Template) + HTMX (파셜 스왑)
두뇌: 진단 엔진 (점수 계산 + 등급 판정 + 불균형 감지) + 결제 검증
얼굴: Tailwind CDN + Canvas RADAR + PILLOW-OG + REVEAL
입출력: SHARE (카카오+텔레그램+X+인스타+html2canvas) + PORTONE (결제)
기억: SQLite (진단 세션, 상품, 주문)
```

**핵심 패턴:**

| 패턴 | 설명 |
|------|------|
| HTMX 파셜 스왑 | 1문항씩 hx-post → 프로그레스 바+문항 함께 교체 |
| HX-Redirect | 마지막 문항 후 full page 이동 (HTMX 중첩 방지) |
| 수능 등급 매핑 | 점수(0~100) → 분위표 기준 1~9등급 |
| 불균형 감지 | max-min gap ≥ 40 → 특수 라벨 ("스펙형 인간") |
| Pillow 동적 OG | 사용자별 결과 PNG 서버사이드 렌더링 |
| IP 중복제거 | 참여자 수 카운팅 (IP 기반 distinct) |
| PortOne 결제 | iamport.js → 서버 금액 검증 → 주문 상태 업데이트 |
| FOMO 세일즈 | 타이머 + 할인율 + 제한 수량 연출 |

**참고 레퍼런스:** [hexaconsulting](references/hexaconsulting.md) (Django+HTMX 연애 컨설팅 퍼널)

---

## 타입 9: 파일 분석기

> "파일 업로드 → 브라우저에서 파싱 → Wrapped 카드 시퀀스로 결과 보여주기"

```
뼈대: BASE + SCREEN
두뇌: Web Worker (파싱) + 룰기반 스코어링 (캐릭터 판정) + REL-TYPE (관계 추정)
얼굴: STYLE-DARK + REVEAL (slamIn+confetti) + CALC (숫자 카운트업)
입출력: SHARE (html2canvas 이미지 저장 + 클립보드 복사)
기억: 없음 (100% 브라우저 로컬, 서버 전송 없음)
```

**핵심 패턴:**

| 패턴 | 설명 |
|------|------|
| Web Worker 파싱 | 대용량 파일 메인 스레드 블로킹 방지 + 프로그레스 보고 |
| 정규식 파서 | 파일 포맷별 정규식으로 구조화 데이터 추출 |
| 룰기반 캐릭터 판정 | 통계 → 임계값 스코어링 → 최고점 캐릭터 선정 (AI 없이) |
| Wrapped 카드 시퀀스 | 전체화면 카드별 그라데이션, 탭 전환, 숫자 카운트업 애니메이션 |
| 관계 유형 추정 (REL-TYPE) | 8계층 신호 가중합산으로 연인/썸/친구/가족/직장 판정 |
| 100% 정적 | 백엔드 없음, 서버 비용 ₩0, GitHub Pages 배포 가능 |

**옵션 부품:**

| 원하는 기능 | 부품 추가 |
|------------|----------|
| 관계 유형 추정 | + REL-TYPE |
| MBTI 추정 | 직접 구현 (tok-wrapped 참고) |

**참고 레퍼런스:** [tok-wrapped](references/tok-wrapped.md) (카카오톡 대화 Wrapped 분석기)

---

## 부품 역할 한눈에

| 부품 | 한마디 | 언제 쓰냐 |
|------|--------|----------|
| [BASE](catalog/base.md) | HTML 껍데기 | 순수 HTML 앱일 때 |
| [SCREEN](catalog/screen.md) | 인트로→진행→결과 전환 | 테스트/계산기 |
| [DATA](catalog/data.md) | JSON으로 데이터 분리 | 질문/세율표/등급 |
| [QUIZ](catalog/quiz.md) | 퀴즈 엔진 | O/X, 선택형 테스트 |
| [CALC](catalog/calc.md) | 계산기 엔진 | 입력→계산→결과 |
| [GRADE](catalog/grade.md) | 등급 판정 | S~F, 티어, 분위 |
| [RADAR](catalog/radar.md) | 레이더 차트 | 다차원 점수 시각화 |
| [TIMER](catalog/timer.md) | 15초 카운트다운 | 긴장감 있는 퀴즈 |
| [REVEAL](catalog/reveal.md) | 결과 두둥 연출 | 극적인 결과 공개 |
| [KAKAO](catalog/kakao.md) | 카톡 공유 | 바이럴 공유 |
| [KAKAO-LOCAL](catalog/kakao-local.md) | 장소 검색 | GPS+맛집 추천 |
| [OG](catalog/og.md) | 공유 미리보기 | SNS 공유 이미지 |
| [SHARE](catalog/share.md) | 통합 공유 | 카톡+URL+스크린샷 |
| [GA](catalog/ga.md) | 방문자 추적 | 트래픽 분석 |
| [URL-ENCODE](catalog/url-encode.md) | 결과를 URL에 | 링크로 결과 공유 |
| [STYLE-DARK](catalog/style-dark.md) | 다크 테마 | 어두운 분위기 |
| [STYLE-LIGHT](catalog/style-light.md) | 라이트 테마 | 밝은 분위기 |
| [LLM](catalog/llm.md) | AI 텍스트 생성 | AI 대화/분석 |
| [RAG](catalog/rag.md) | 지식 검색+주입 | AI에 전문지식 부여 |
| [TELEGRAM](catalog/telegram.md) | 텔레그램 봇 | 챗봇/알림 |
| [TWILIO](catalog/twilio.md) | 전화/SMS 알림 | 긴급 알림 |
| [POCKETBASE](catalog/pocketbase.md) | DB+인증+API | 빠른 백엔드 |
| [REDIS](catalog/redis.md) | 캐시+세션+대화기억 | AI 챗봇 |
| [DYNAMIC-PROMPT](catalog/dynamic-prompt.md) | 동적 프롬프트 조립 | AI 챗봇 변수 주입 |
| [DJANGO](catalog/django.md) | Django 풀스택 | 서버 렌더링 앱 |
| [HTMX](catalog/htmx.md) | 서버 HTML 부분 교체 | SPA 같은 UX |
| [PORTONE](catalog/portone.md) | PG 결제 | 상품 결제 |
| [PILLOW-OG](catalog/pillow-og.md) | 동적 OG 이미지 | 개인화 공유 썸네일 |
| [REL-TYPE](catalog/rel-type.md) | 관계 유형 추정 | 채팅 관계 분석 |
| [DEPLOY](catalog/deploy.md) | EC2 배포 | 서버에 올리기 |

---

## 뭘 할 때 뭘 봐야 하나

| 상황 | 참고할 곳 |
|------|----------|
| "이런 앱 만들고 싶어" | → 이 페이지에서 **앱 타입** 골라서 부품 조합 |
| "이 부품 어떻게 쓰지?" | → [모듈 카탈로그](catalog/README.md)에서 해당 모듈 클릭 |
| "비슷한 앱 코드 보고 싶어" | → [레퍼런스](references/README.md)에서 가장 비슷한 앱 |
| "전체 기술 한눈에 보고 싶어" | → [기술 지도](tech-map.md) |
| "새 프로젝트 분석해서 추가" | → [AI 지침서](INSTRUCTIONS.md) |
| "이 기술 어떻게 세팅하지?" | → [레시피](recipes/github-upload.md) |
| "이거 왜 안 돼?" | → [삽질 방지](gotchas/tailwind-v4.md) |
| "서버가 죽었어" | → [EC2 OOM](gotchas/ec2-oom-swap.md) + [보안](gotchas/ec2-security.md) |
| "GitHub에 올리는 법" | → [GitHub 업로드](recipes/github-upload.md) |

---

## AI한테 던지는 법

```
playbook의 조립 가이드를 보고
"___" 앱을 만들어줘.

타입: [바이럴 테스트 / 계산기 / 추천기 / AI 챗봇 / 알림 봇 / 업무 도구 / 커뮤니티 플랫폼 / 세일즈 퍼널 / 파일 분석기]
부품: [필요한 모듈 나열]
참고: [가장 비슷한 레퍼런스]
테마: [다크 / 라이트]
추가: [특별 요구사항]
```
