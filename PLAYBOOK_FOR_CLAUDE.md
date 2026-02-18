# PLAYBOOK FOR CLAUDE — 압축 레퍼런스
> 이 파일은 playbook 전체(26 모듈, 18 레퍼런스, 7 레시피, 5 삽질방지)를 Claude가 매 세션 읽을 수 있도록 압축한 것.
> 원본: C:\Users\ganna\Downloads\playbook | 웹: https://ganna40.github.io/playbook
> 마지막 동기화: 2026-02-18 (poli 추가)

---

## 1. 모듈 카탈로그 (26개) — 핵심 코드 패턴

### BASE — SPA 골격
단일 HTML, `max-width:480px`, `user-scalable=no`, CDN 라이브러리.
```html
<div id="app">
  <div id="screen-intro" class="screen active"></div>
  <div id="screen-progress" class="screen"></div>
  <div id="screen-result" class="screen"></div>
</div>
```
```css
.screen{display:none} .screen.active{display:block;animation:fadeIn .35s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
```

### SCREEN — 화면 전환
```javascript
function showScreen(name) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(`screen-${name}`).classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
```

### DATA — JSON 분리
```javascript
let appData = null;
async function loadData() {
  appData = await (await fetch('data.json')).json();
  initApp();
}
document.addEventListener('DOMContentLoaded', loadData);
```
표준 구조: `{ meta:{}, questions:[], grades:[], categories:[], config:{kakaoKey, gaId, domain} }`

### QUIZ — 퀴즈 엔진
**O/X (pong):** `questions[{id,c,q,bs,killer}]` → answered=true면 bs 가산, combo/correlation 보너스
**선택형 (mz/amlife):** `questions[{id,c,q,options:[{text,score}]}]` → 카테고리별 합산 → 백분율
```javascript
let currentIndex = 0, answers = {};
function selectAnswer(value) {
  answers[quizData.questions[currentIndex].id] = value;
  if (++currentIndex >= quizData.questions.length) calculateResult();
  else showQuestion(currentIndex);
}
// 프로그레스: bar.style.width = ((currentIndex+1)/total*100)+'%'
```

### CALC — 계산기
입력 포맷팅: `e.target.value.replace(/[^\d]/g,'')` → `Number(val).toLocaleString('ko-KR')`
세금 룩업: `for(i=table.length-1;i>=0;i--) if(salary>=table[i][0]) return table[i][1]`
숫자 카운트업:
```javascript
function animateNumber(el, target, duration=1000) {
  const start=performance.now();
  (function update(t) {
    const p=Math.min((t-start)/duration,1), eased=1-Math.pow(1-p,3);
    el.textContent=Math.floor(target*eased).toLocaleString('ko-KR');
    if(p<1) requestAnimationFrame(update);
  })(start);
}
```

### GRADE — 등급 시스템
```javascript
// data: grades:[{min,max,id,name,emoji,color,ogImage}]
function determineGrade(score) {
  return quizData.grades.find(g => score>=g.min && score<=g.max) || quizData.grades.at(-1);
}
// 결과 카드: grade-badge(emoji+name) + title + desc + score
// OG 동적교체: meta[og:image].content = grade.ogImage
```

### RADAR — Canvas 레이더 차트
```javascript
function drawRadarChart(canvasId, categories, scores, options={}) {
  const canvas=document.getElementById(canvasId), ctx=canvas.getContext('2d');
  const W=canvas.width=options.size||300, H=canvas.height=W;
  const cx=W/2, cy=H/2, R=Math.min(cx,cy)-40, n=categories.length;
  const angles=categories.map((_,i)=>(Math.PI*2*i/n)-Math.PI/2);
  const color=options.color||'#3182f6';
  // 5단계 그리드 + 축선 + 데이터 폴리곤(fill alpha 20%) + 포인트(arc 4px) + 라벨(R+24)
  // scores는 0~100 범위, 카테고리 6~8개 최적
}
```

### TIMER — 15초 카운트다운
```javascript
let TIMER_ID=null, TIMER_SEC=15;
function startTimer() {
  clearInterval(TIMER_ID); TIMER_SEC=15;
  const bar=document.getElementById('timerBar');
  bar.style.transition='none'; bar.style.width='100%';
  void bar.offsetWidth; // force reflow (핵심!)
  bar.style.transition='width 1s linear';
  TIMER_ID=setInterval(()=>{
    if(--TIMER_SEC<=5) bar.classList.add('urgent');
    bar.style.width=(TIMER_SEC/15*100)+'%';
    document.getElementById('timerNum').textContent=TIMER_SEC;
    if(TIMER_SEC<=0){clearInterval(TIMER_ID);autoAnswer();}
  },1000);
}
```

### REVEAL — 극적 결과 공개
패턴: 분석중(2초) → 오버레이 흔들림(0.8초) → 등급 슬램 + 컨페티(1.7초) → 결과화면
```css
@keyframes slamIn{0%{transform:scale(3);opacity:0}60%{transform:scale(.9)}100%{transform:scale(1);opacity:1}}
@keyframes glitchIn{0%{opacity:0;transform:scale(3) skewX(20deg)}20%{opacity:1;transform:scale(.8) skewX(-10deg)}100%{transform:scale(1) skewX(0)}}
@keyframes confettiFall{0%{transform:translateY(-100vh) rotate(0)}100%{transform:translateY(100vh) rotate(720deg)}}
```
좋은등급: fadeScale+금컨페티 / 나쁜등급: glitchIn+빨간플래시
컨페티: 40개 div, random position/size/color, `position:fixed;top:-10px;pointer-events:none`

### SHARE — 통합 공유
의존: KAKAO, OG, html2canvas
```javascript
// 카카오: Kakao.Share.sendDefault({objectType:'feed',content:{title,description,imageUrl,link:{mobileWebUrl,webUrl}},buttons:[{title:'나도 해보기',link}]})
// URL복사: navigator.clipboard.writeText(url).catch(()=>{textarea fallback})
// 스크린샷: html2canvas(card,{scale:2,backgroundColor:'#0a0a0f',useCORS:true}) → a.download='결과.png'
// 주의: 버튼 숨기기→캡처→복원, iOS clipboard fallback 필수
```

### KAKAO — 카카오톡 SDK
```html
<script src="https://t1.kakaocdn.net/kakao_js_sdk/2.7.4/kakao.min.js"></script>
```
`if(!Kakao.isInitialized()) Kakao.init('APP_KEY')` — 1회만, 도메인 등록 필수, imageUrl은 https 절대경로

### OG — Open Graph
```html
<meta property="og:type" content="website">
<meta property="og:title/description/url/image" content="...">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
```
이미지 1200x630px PNG 300KB이하. 카카오 캐싱 → URL 변경 시 `?v=2`

### URL-ENCODE — 결과 URL 공유
```javascript
// 인코딩: answers.map(a=>a>=0?a:0).join('') → ?r=01230123&a=25&g=M
// MZ방식: ?d=199502101230 (4자리연도+답변)
// 디코딩: URLSearchParams → answers 복원 → 바로 결과화면
// 재시작: history.replaceState(null,'',location.pathname)
```

### GA — Google Analytics 4
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','G-XXXXXXXXXX');</script>
```
이벤트: `gtag('event','quiz_complete',{grade,score})`, `gtag('event','share',{method:'kakao'})`

### STYLE-DARK — 다크 테마 (pong 스타일)
```css
:root{--bg:#0a0a0f;--card:#14141f;--card2:#1a1a2e;--border:#2a2a3e;--t1:#fff;--t2:#a0a0b8;--t3:#6b6b80;--accent:#7c3aed;--accent2:#a855f7;--danger:#ef4444;--safe:#22c55e}
body{background:var(--bg);color:var(--t1);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans KR',sans-serif}
.btn-primary{background:linear-gradient(135deg,var(--accent),var(--accent2));border-radius:14px;padding:16px}
```

### STYLE-LIGHT — 라이트 테마 (salary/mz 스타일)
```css
:root{--bg:#f4f5f7;--card:#fff;--border:#eceef1;--t1:#191f28;--t2:#4e5968;--accent:#3182f6;--shadow:0 1px 3px rgba(0,0,0,.04)}
body{background:var(--bg);color:var(--t1);font-family:'Pretendard Variable',Pretendard,-apple-system,sans-serif}
```
Pretendard: `<link href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">`

### LLM — AI 텍스트 생성
**Ollama(로컬):** `POST http://localhost:11434/api/generate` json={model,prompt,system,stream,options:{temperature,top_p}}
**OpenAI(클라우드):** `POST https://api.openai.com/v1/chat/completions` headers=Bearer, json={model,messages,temperature}
**OpenRouter:** `POST https://openrouter.ai/api/v1/chat/completions` 동일 형식
**SSE 스트리밍:** FastAPI StreamingResponse + `async for line in response.aiter_lines()`
**듀얼 프로바이더:** BaseLLMService ABC → OllamaService / OpenRouterService, 런타임 switch
모델: gemma3:4b(범용) / exaone3.5:7.8b(한국어) / gpt-4o-mini(클라우드경제적) / nomic-embed-text(임베딩768d)

### RAG — 벡터 검색 파이프라인
흐름: 텍스트→청킹(1500자)→임베딩→pgvector 저장 / 질문→임베딩→코사인유사도검색→Top-K→LLM 컨텍스트 주입
```python
# pgvector 검색: SELECT content, 1-(embedding<=>:embedding) as similarity FROM chunks WHERE similarity>:threshold ORDER BY embedding<=>:embedding LIMIT :top_k
# 임베딩: Ollama nomic-embed-text(768d) 또는 sentence-transformers E5-large(1024d)
# E5 prefix 필수: "query: "+text (검색시) / "passage: "+text (저장시)
# 인덱스: <100행 HNSW, >=100행 IVFFlat
```

### DYNAMIC-PROMPT — 동적 프롬프트 빌더
**패턴1 변수주입:** `TEMPLATE.format(**vars_dict)` 기본값 필수
**패턴2 컨텍스트스택:** `prompt_parts=[]` → 조건부 append → `"\n".join(prompt_parts)`
7레이어: 페르소나→사용자정보→태도분기→RAG결과→제약조건→대화히스토리→현재메시지
**패턴3 모드감지:** 키워드→scores dict→max score 모드 선택
**패턴4 오버라이드:** 맨 마지막에 최우선 지시 (LLM recency bias 활용)

### TELEGRAM — 텔레그램 봇
```python
# python-telegram-bot 21: Application.builder().token(T).build()
# CommandHandler("start",fn) + MessageHandler(filters.TEXT,fn) + CallbackQueryHandler(fn)
# send_action("typing"), reply_text(), InlineKeyboardMarkup
# 그룹: @bot_username 멘션 or 답글일때만 응답
# 배포: systemd service, Restart=always
# 메시지 최대 4096자, 봇 토큰 비공개
```

### TWILIO — 전화/SMS
```python
# 전화: client.calls.create(twiml='<Response><Say language="ko-KR">메시지</Say></Response>',to='+82...',from_='+1...')
# SMS: client.messages.create(body='메시지',to='+82...',from_='+1...')
```

### POCKETBASE — BaaS
REST API: `GET/POST/PATCH/DELETE /api/collections/{name}/records`
인증: `POST /api/collections/users/auth-with-password` → token
파일: multipart/form-data 업로드

### REDIS — 캐시/세션/대화기억
```python
# 대화 히스토리: redis.lpush(f"chat:{id}", json.dumps(msg)); redis.ltrim(f"chat:{id}", 0, 9); redis.expire(f"chat:{id}", 86400)
# 캐시: redis.setex(key, ttl, value)
```

### DJANGO — 풀스택
Model(ORM) + View + Template + Signal(post_save) + Admin + Middleware + Management Command
HTMX 분기: `if request.headers.get('HX-Request'): return render(request,'partial.html',ctx)`
`select_related()` 필수 (N+1 방지), JSONField, Custom Template Tag

### HTMX — 서버 HTML 부분교체
```html
<script src="https://unpkg.com/htmx.org@2.0.4"></script>
<body hx-headers='{"X-CSRFToken":"{{csrf_token}}"}'>
<!-- hx-post="/url" hx-target="#target" hx-swap="innerHTML" -->
```
마지막 문항 → `HX-Redirect` 헤더로 전체 페이지 이동

### PORTONE — PG 결제
```javascript
// IMP.init('MERCHANT_ID'); IMP.request_pay({pg:'html5_inicis',pay_method:'card',amount,name,buyer_tel})
// 서버: POST /verify → PortOne REST API로 금액 검증 → 주문 상태 업데이트
```

### PILLOW-OG — 동적 OG 이미지
```python
# Pillow: Image.new('RGB',(800,800),bg) → ImageDraw.text() → NotoSansCJK 폰트
# 사용자별 결과 PNG 서버사이드 생성 → /og/{session_key}.png 로 서빙
```

### DEPLOY — EC2 배포
```bash
scp -i key.pem -r ./project/* ubuntu@IP:/var/www/프로젝트명/
# Nginx: server{listen 80;server_name sub.pearsoninsight.com;root /var/www/프로젝트명;try_files $uri $uri/ =404}
# symlink → nginx -t → reload → Cloudflare A레코드(프록시ON)
```

---

## 2. 레퍼런스 프로젝트 (19개) — 프로필 카드

| # | 프로젝트 | 유형 | 스택 | 모듈 조합 | 특수 기능 |
|---|----------|------|------|-----------|-----------|
| 1 | **salary** | 계산기 | Vanilla+Tailwind CDN+Pretendard | BASE+DATA+SCREEN+CALC+GRADE+SHARE+GA+STYLE-LIGHT | 4대보험/소득세 룩업, LoL 티어, 소득분위 |
| 2 | **pong** | O/X진단 | Vanilla+시스템폰트 | BASE+DATA+SCREEN+QUIZ+GRADE+SHARE+GA+STYLE-DARK | 36문항, 콤보/상관관계/킬러, 시그마~오메가6등급 |
| 3 | **mz** | 선택형다차원 | Vanilla+Pretendard+Canvas | BASE+QUIZ+GRADE+RADAR+SHARE+GA+STYLE-LIGHT | 40문항5지선다→8차원, SSS~F7등급, 세대비교, URL공유 |
| 4 | **amlife** | 선택형다차원 | Vanilla+시스템폰트+Canvas | BASE+DATA+QUIZ+GRADE+RADAR+SHARE+GA+STYLE-LIGHT | 60문항4지선다→8차원, 나이가중치, S~F6등급 |
| 5 | **food** | GPS추천기 | Svelte5+TS+Vite7+Tailwind v3 | 커스텀 | Kakao Local API, GPS, 별점필터, 거부목록, Vite프록시 |
| 6 | **tarot** | AI타로상담 | React18+FastAPI+pgvector+Ollama | LLM+RAG | 78장 셔플, 3D카드, RAG5소스, SSE, 가드레일, Docker |
| 7 | **psycho-bot** | AI심리봇 | FastAPI+pgvector+E5-1024d+Ollama+Telegram | LLM+RAG+REDIS+DYNAMIC-PROMPT+TELEGRAM | 5모드, 위기감지3단계, 자기인식, 학습DB, 그룹채팅 |
| 8 | **telbot** | 알림봇 | FastAPI+Telegram+Twilio | TELEGRAM+TWILIO | UUID반복알림, 인메모리, Twilio에스컬레이션 |
| 9 | **collab-tool** | 팀대시보드 | Flask+PocketBase+Bootstrap5+Chart.js | Flask+POCKETBASE | KPI가중평균, Burn-up, FullCalendar, JARVIS Glassmorphism |
| 10 | **product-j** | 엑셀분석 | Python+pandas+openpyxl | CLI스크립트 | NULL기반 재고판별, 피벗테이블 |
| 11 | **error-automation** | SRE자동화 | FastAPI+Ollama+Telegram+Twilio+SQLite | LLM+TELEGRAM+TWILIO | 3단계보고서, 자연어수정, 온콜에스컬레이션 |
| 12 | **human2** | 페르소나봇 | Ollama+pgvector+Redis+ko-sroberta+Telegram | LLM+RAG+REDIS+DYNAMIC-PROMPT+TELEGRAM | 469만 카톡ETL, 7단계동적프롬프트, 듀얼메모리 |
| 13 | **dictionary** | CLI위자드 | Go+MySQL+Vanilla JS | Go net/http+go:embed | 단일바이너리9.6MB, CLI exec, bcrypt세션 |
| 14 | **rackops** | DCIM | Svelte+Vite+Tailwind+D3.js+FastAPI+Paramiko+PySNMP | 커스텀 | 비주얼랙42U, SSH/SNMP모니터링, 네트워크토폴로지 |
| 15 | **hexalounge** | 매칭커뮤니티 | Django6+HTMX+Tailwind CDN+Alpine.js | DJANGO+HTMX+RADAR+GRADE | 6인증, 3Tier매칭, Elo인기도, 양방향좋아요 |
| 16 | **hexaconsulting** | 세일즈퍼널 | Django6+HTMX+Pillow+PortOne | DJANGO+HTMX+RADAR+PILLOW-OG+PORTONE | 20문항HTMX파셜, 수능등급, 동적OG, PG결제, FOMO |
| 17 | **tok-wrapped** | 파일분석기 | Vanilla+Pretendard+WebWorker | BASE+SCREEN+GRADE+REVEAL+SHARE+STYLE-DARK | 카카오톡.txt파싱, 16캐릭터룰기반판정, 8장Wrapped카드, 컨페티, 100%정적(백엔드없음) |
| 18 | **vibejob** | 프리랜서매칭 | Next.js15+React19+Prisma+NextAuth+Tailwind v4+shadcn/ui | 커스텀(풀스택) | AI견적(Claude), 에스크로결제, 등급시스템, 채팅, S3파일업로드, 코드리뷰카테고리 |
| 19 | **poli** | 정치성향테스트 | Vanilla+Pretendard+Canvas+Python http.server+SQLite | BASE+SCREEN+QUIZ+TIMER+GRADE+RADAR+REVEAL+SHARE+OG+URL-ENCODE+CALC+STYLE-DARK | 12문항5축양방향채점, 7단계강도, 20초타이머, URL결과공유, 고유IP카운터(SHA256), Pillow OG이미지, Cloudflare+Apache배포 |

---

## 3. 앱 타입별 조립 공식

| 타입 | 공식 | 난이도 |
|------|------|--------|
| **바이럴 테스트** | BASE+SCREEN+DATA+QUIZ+TIMER+GRADE+REVEAL+SHARE+GA+STYLE | ★☆☆ |
| **계산기** | BASE+SCREEN+DATA+CALC+GRADE+SHARE+GA+STYLE-LIGHT | ★☆☆ |
| **추천기** | Svelte/React+Vite+Tailwind+외부API+Geolocation | ★★☆ |
| **AI 챗봇** | FastAPI+LLM+RAG+DYNAMIC-PROMPT+REDIS+TELEGRAM | ★★★ |
| **알림 봇** | FastAPI+TELEGRAM+TWILIO+인메모리dict | ★★☆ |
| **업무 도구** | Flask+POCKETBASE+Bootstrap5+Chart.js+FullCalendar | ★★★ |
| **커뮤니티** | DJANGO+HTMX+Tailwind CDN+Alpine.js+RADAR+GRADE | ★★★ |
| **세일즈 퍼널** | DJANGO+HTMX+RADAR+PILLOW-OG+PORTONE+SHARE | ★★☆ |
| **파일 분석기** | BASE+SCREEN+GRADE+REVEAL+SHARE+STYLE-DARK+WebWorker | ★☆☆ |
| **프리랜서 매칭** | Next.js15+React19+Prisma+NextAuth+Tailwind v4+shadcn/ui+S3 | ★★★ |

---

## 4. 삽질 방지 (핵심만)

**Tailwind v4:** `@import "tailwindcss"` → preflight 포함. `*{margin:0;padding:0}` 절대 추가 금지 (px-6 등 무효화). 설정: `@theme{--color-name:값}` CSS에서. Vite: `@tailwindcss/vite` 플러그인 (PostCSS 불필요).

**CSS Overflow:** Grid/Flex 자식 `min-width:auto` 기본값 → 부모 뚫고 나감. 해결: `min-w-0` 모든 자식에. 중첩 시 매 레벨마다.

**Windows SSH:** PEM 권한: `icacls key.pem /inheritance:r /grant:r "%USERNAME%:R"`. AMI유저: Ubuntu=ubuntu, Amazon=ec2-user. Git Bash 경로 변환: `C:\` → `/c/`.

**EC2 OOM:** Swap 2GB: `fallocate -l 2G /swapfile && chmod 600 && mkswap && swapon && fstab`. MySQL 다이어트: `innodb_buffer_pool_size=128M, max_connections=30`.

**EC2 보안:** feroxbuster 등 스캐너 UA 차단(.htaccess RewriteCond), `iptables -A INPUT -s IP -j DROP` + `iptables-persistent`, xmlrpc.php 차단.

---

## 5. 레시피 (핵심만)

**React+Vite+Tailwind v4:** `npm create vite@latest -- --template react-ts` → `npm install tailwindcss @tailwindcss/vite` → vite.config에 플러그인 추가 → index.css에 `@import "tailwindcss"; @theme{...}` → postcss.config 불필요

**Django+HTMX+Tailwind CDN:** pip install django → startproject → startapp → `<script src="cdn.tailwindcss.com">` + `tailwind.config={theme:{extend:{colors:{...}}}}` + `<script src="unpkg.com/htmx.org@2.0.4">` + `<body hx-headers='{"X-CSRFToken":"{{csrf_token}}"}'>`

**Flask+SSE 실시간:** `jobs={}` dict → threading.Thread(target=do_work) → `/api/job/{id}/stream` → `Response(generate(), mimetype="text/event-stream")` → 프론트 EventSource

**EC2 배포:** SCP 업로드 → Nginx 설정 → symlink → reload → Cloudflare DNS A레코드 프록시ON

**GitHub:** `git init && git add -A && git commit -m "init" && gh repo create name --private --source=. --push`

---

## 6. 인프라 정보

| 항목 | 값 |
|------|-----|
| 서버 | EC2 (Ubuntu), Web root: /var/www/ |
| 도메인 | *.pearsoninsight.com (Cloudflare) |
| GitHub | ganna40, GCM 자동인증 |
| Git | "C:\Program Files\Git\cmd\git.exe" |
| git-uploader | C:\Users\ganna\Downloads\git-uploader (python app.py) |
| SSH/서버정보 | _secrets.md 참조 (playbook 로컬) |

---

## 7. AI에게 프로젝트 주문하는 방법

```
이 PLAYBOOK_FOR_CLAUDE.md를 참고해서 "___" 앱을 만들어줘.
타입: [바이럴테스트 | 계산기 | 추천기 | AI챗봇 | 알림봇 | 업무도구 | 커뮤니티 | 세일즈퍼널]
테마: [다크 | 라이트]
모듈: [QUIZ+TIMER+GRADE+REVEAL+SHARE+...]
참고 레퍼런스: [pong | mz | salary | ...]
추가 요구: ...
```

---

## 8. 이 파일 업데이트 방법

새 프로젝트/모듈이 playbook에 추가될 때:

1. **새 모듈:** 섹션1에 `### 모듈명 — 한줄설명` + 핵심 코드패턴(10~20줄) 추가
2. **새 레퍼런스:** 섹션2 테이블에 한 행 추가 (`프로젝트|유형|스택|모듈조합|특수기능`)
3. **새 조립공식:** 섹션3 해당되면 추가
4. **새 삽질방지:** 섹션4에 한 줄 추가
5. **동기화 날짜:** 파일 상단 날짜 업데이트

**추가 원칙:**
- 모듈은 핵심 함수 시그니처 + 최소 코드만 (설명 최소화)
- 레퍼런스는 테이블 한 행으로 압축
- 상세 코드가 필요하면 원본 playbook 파일을 직접 읽기
