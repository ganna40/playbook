# Playbook 운영 지침서

> **이 파일을 Claude(또는 다른 AI)에게 던지면 바로 작업 가능.**
> 새 프로젝트를 분석하거나, 기존 playbook을 업데이트하거나, 모듈을 조합해서 새 앱을 만들 때 사용.

---

## 이게 뭐냐

개발하면서 배운 기술들을 **모듈 카탈로그**로 표준화해놓은 개인 레시피북이다.
레고 블록처럼 모듈을 조합하면 AI가 앱을 한번에 만들 수 있다.

## 어디 있냐

| 항목 | 위치 |
|------|------|
| GitHub | https://github.com/ganna40/playbook |
| 웹사이트 | https://ganna40.github.io/playbook |
| 로컬 | C:\Users\ganna\Downloads\playbook |
| Docsify 기반 | index.html + 마크다운 파일들 |

## 민감 정보

> **서버 IP, SSH 키, API 키 등 민감 정보는 공개 파일에 넣지 마.**
> 실제 값은 로컬 전용 파일 `_secrets.md`에 있음 (gitignore됨).
> 배포나 서버 작업이 필요하면 사용자에게 `_secrets.md` 내용을 달라고 해.

## 보안 기본 규칙

> **웹서비스를 만들거나 분석하거나 배포할 때는 항상 먼저 [웹서비스 보안 체크리스트](recipes/web-security-checklist.md)를 확인해라.**
> 이 규칙은 새 프로젝트 생성, 기존 프로젝트 분석, 운영 배포, 관리자 페이지 추가 작업 모두에 적용된다.

- 새 웹서비스 제작: 구현 전에 체크리스트를 읽고 구조를 잡는다
- 기존 프로젝트 분석: 기능 분석과 별개로 보안 항목도 같이 진단한다
- 배포 직전: 보안 체크리스트의 "운영 전 최종 점검표"를 반드시 수행한다
- 관리자 경로(`/admin`, `/internal`)나 관리자 API가 있으면 접근 제어를 기본 요구사항으로 취급한다
- secret, env, token, 결제/권한 검증, 에러 노출, CORS, 보안 헤더는 항상 점검 범위에 포함한다

## 폴더 구조

```
playbook/
├── index.html          # Docsify 설정 (건드리지 마)
├── _sidebar.md         # 사이드바 네비게이션
├── _secrets.md         # ★ 민감 정보 (gitignore됨, 공개 안됨)
├── README.md           # 홈페이지
├── tech-map.md         # ★ 기술 지도 (한눈에 보기)
├── INSTRUCTIONS.md     # ★ 이 파일 (AI 지침서)
│
├── catalog/            # 모듈 카탈로그 (빌딩블록)
│   ├── README.md       # 모듈 목록 + 조합 예시
│   ├── base.md         # SPA 기본 골격
│   ├── data.md         # JSON 데이터 분리
│   ├── screen.md       # 화면 전환
│   ├── quiz.md         # 퀴즈/설문 엔진
│   ├── calc.md         # 계산기 엔진
│   ├── grade.md        # 등급/티어 시스템
│   ├── radar.md        # 레이더 차트
│   ├── timer.md        # 질문 타이머
│   ├── reveal.md       # 결과 공개 연출
│   ├── url-encode.md   # 결과 URL 공유
│   ├── kakao.md        # 카카오톡 공유
│   ├── og.md           # Open Graph
│   ├── share.md        # 통합 공유
│   ├── ga.md           # Google Analytics
│   ├── style-dark.md   # 다크 테마
│   ├── style-light.md  # 라이트 테마
│   ├── swipe.md        # 스와이프 답변 (Tinder식)
│   ├── spectrum.md     # 슬라이더 답변 (0~100)
│   ├── drag-rank.md    # 드래그 순위 매기기
│   ├── capture.md      # 결과 이미지 캡처 (html2canvas)
│   ├── sound.md        # 효과음 (Web Audio API)
│   ├── haptic.md       # 햅틱 피드백 (Vibration API)
│   └── deploy.md       # EC2 배포
│
├── references/         # 실제 만든 앱 분석
│   ├── README.md       # 레퍼런스 목록
│   ├── salary.md       # 월급계산기
│   ├── pong.md         # 퐁퐁측정기
│   ├── mz.md           # MZ력측정기
│   ├── amlife.md       # 엠생력측정기
│   └── love.md         # 연애유형테스트
│
├── recipes/            # 기술별 How-to
│   ├── flask-dashboard.md
│   ├── server-to-github.md
│   └── react-vite-tailwind.md
│
└── gotchas/            # 삽질 방지
    ├── tailwind-v4.md
    ├── windows-ssh.md
    └── css-overflow.md
```

---

## 작업 유형별 지시

### 1. "새 프로젝트를 분석해서 playbook에 추가해줘"

이건 가장 자주 하는 작업이다. **아래 단계를 빠짐없이 따라라.**

> 시작하기 전에: [웹서비스 보안 체크리스트](recipes/web-security-checklist.md)를 먼저 읽고, 분석 결과에 보안 진단 항목을 포함해라.

#### 1단계: 프로젝트 코드 읽기

사용자가 프로젝트 경로를 알려줄 거다. 아래 파일들을 **반드시** 읽어라:

```
필수:
  index.html          ← HTML 구조, <head> 태그 (CDN, 폰트, 메타태그)
  *.js / script.js    ← 핵심 로직 (화면 전환, 점수 계산, API 호출)
  *.css / style.css   ← CSS 방식 (Tailwind? 순수 CSS? CSS Variables?)
  data.json           ← 있으면 데이터 구조 분석

선택:
  og-*.png            ← OG 이미지 파일명 패턴
  기타 정적 파일       ← 이미지, 폰트 등
```

#### 2단계: 기술 추출 체크리스트

코드를 읽으면서 **아래 항목들을 하나씩 확인**하고 채워라:

```
□ 앱 유형: [계산기 / O/X 퀴즈 / 선택형 퀴즈 / 기타]
□ CSS 방식: [Tailwind CDN / 순수 CSS / CSS Variables / 인라인]
□ 폰트: [Pretendard CDN / 시스템 폰트 / 기타]
□ 테마: [다크 / 라이트] + 악센트 색상
□ 데이터: [JSON 분리(fetch) / 인라인(JS 내장)]
□ 차트: [Canvas 레이더 / 없음 / 기타]
□ Kakao SDK: [있음 → 키 확인] / [없음]
□ GA: [있음 → ID 확인] / [없음]
□ html2canvas: [있음 / 없음]
□ Web Share API: [있음 / 없음]
□ 타이머: [있음 → 몇초?] / [없음]
□ 결과 공개 연출: [있음 → 애니메이션 종류] / [없음]
□ URL 인코딩: [있음 → 인코딩 방식] / [없음]
□ 등급 시스템: [있음 → 등급 이름들] / [없음]
□ 성별 분기: [있음 / 없음]
□ 특수 기능: [콤보, 상관관계, 킬러문항, 나이 가중치 등]
□ 보안: [secret 노출 / 관리자 경로 / 관리자 API / 에러 노출 / CORS / source map / 결제검증 / RLS]
```

#### 3단계: 기존 모듈과 비교 + 새 모듈 생성

`catalog/README.md`의 모듈 목록을 보고:
- **기존 모듈로 설명 가능** → 레퍼런스만 추가
- **새로운 기술/패턴 발견** → **반드시** 새 모듈 파일 생성 (아래 모듈 템플릿 따라)

> **중요: 새로운 API, 라이브러리, 패턴이 있으면 무조건 모듈로 만들어라.**
> 예시: 카카오 Local API, Geolocation, Framer Motion, pgvector 등
> "다른 프로젝트에서도 재사용할 수 있는 기술"이면 모듈 후보다.

#### 4단계: 파일 생성/업데이트

아래 파일들을 **빠짐없이** 업데이트한다:

| 순서 | 파일 | 할 일 |
|------|------|-------|
| 1 | `references/새프로젝트.md` | 새로 생성 (아래 레퍼런스 템플릿) |
| 2 | `references/README.md` | 목록 테이블에 한 줄 추가 |
| 3 | `tech-map.md` — 기술 카테고리 | 새로운 기술이 있으면 해당 카테고리 테이블에 추가 |
| 4 | `tech-map.md` — 매트릭스 | 새 앱 열(column) 추가, ✅ 체크 |
| 5 | `tech-map.md` — 프로필 카드 | 새 프로필 카드 블록 추가 |
| 6 | `catalog/README.md` | 새 모듈 있으면 테이블에 추가 |
| 7 | `catalog/새모듈.md` | 새 모듈 있으면 파일 생성 |
| 8 | `recipes/새레시피.md` | 새로운 개발 패턴/세팅 방법이 있으면 레시피 추가 |
| 9 | `gotchas/새삽질방지.md` | 삽질한 경험/주의사항이 있으면 삽질방지 추가 |
| 10 | `_sidebar.md` | 레퍼런스 + 새 모듈 + 레시피 + 삽질방지 네비게이션에 추가 |
| 11 | `builder.md` | 새 앱 타입이면 조립 가이드에 타입/부품 조합 추가 |

> **레시피 후보**: 새로운 기술 조합의 세팅 방법, 배포 파이프라인, 개발환경 구성 등
> 예시: Svelte+Vite 세팅, Docker Compose 개발환경, Telegram 봇 배포 등
>
> **삽질방지 후보**: 실제로 겪은 버그, 설정 실수, 환경 차이 문제 등
> 예시: API 키 노출, CORS 에러, 메모리 부족, 보안 취약점 등

#### 5단계: 검증

- [ ] 레퍼런스 파일에 모듈 조합이 정확한가?
- [ ] tech-map.md 매트릭스에 누락된 기술이 없는가?
- [ ] _sidebar.md에 새 항목이 **모두** 추가되었는가? (레퍼런스, 모듈, 레시피, 삽질방지)
- [ ] 민감 정보(API 키, 서버 IP 등)가 공개 파일에 없는가?
- [ ] 새로운 개발 패턴이 레시피로 추가되었는가?
- [ ] 삽질한 경험이 삽질방지로 추가되었는가?
- [ ] 웹서비스라면 [웹서비스 보안 체크리스트](recipes/web-security-checklist.md) 기준으로 보안 점검을 수행했는가?

#### 6단계: Git 업데이트

```bash
cd C:\Users\ganna\Downloads\playbook
git add -A
git commit -m "add: 새프로젝트 레퍼런스 + 분석"
git push origin main
```

---

**레퍼런스 템플릿:**

```markdown
# 프로젝트명 - 한줄 설명

> URL: https://subdomain.pearsoninsight.com
> GitHub: https://github.com/ganna40/프로젝트명

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 계산기 / O/X 테스트 / 선택형 테스트 / 기타 |
| **한줄 설명** | 뭘 하는 앱인지 |
| **타겟** | 누구를 위한 건지 |
| **테마** | 다크 / 라이트 |
| **폰트** | Pretendard / 시스템 폰트 / 기타 |

## 모듈 조합

\```
BASE + DATA + QUIZ + TIMER + GRADE + REVEAL + SHARE + GA + STYLE-DARK
\```

## 특수 기능

| 기능 | 설명 |
|------|------|
| ... | ... |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| ... | ... |

## data.json 구조

\```
data.json
├── ...
\```

## AI에게 비슷한 거 만들게 하려면

\```
playbook의 {프로젝트명} 레퍼런스를 보고
"{새 앱 이름}"을 만들어줘.
[모듈 조합] 조합.
...
\```
```

---

### 2. "새 모듈을 발견했어, 카탈로그에 추가해줘"

**모듈 파일 템플릿:**

```markdown
# [모듈명] 한줄 설명

> 언제 쓰는지 설명.
> 의존: [다른 모듈] (있으면)

## 필요 라이브러리

\```html
<script src="..."></script>
\```

## 핵심 코드

\```javascript
// 복붙 가능한 코드
\```

## CSS

\```css
/* 필요한 스타일 */
\```

## 주의사항

- 주의할 점 목록

## 사용 예시

\```javascript
// 실제 사용법
\```
```

**업데이트할 파일:**
- `catalog/새모듈.md` 생성
- `catalog/README.md` 테이블에 추가
- `tech-map.md` 해당 카테고리에 추가
- `_sidebar.md` 에 추가

### 3. "이 모듈들 조합해서 새 앱 만들어줘"

1. `tech-map.md`에서 지정된 모듈 확인
2. 각 모듈의 catalog 파일에서 코드 패턴 가져오기
3. 참고 레퍼런스가 있으면 해당 앱 구조 따르기
4. [웹서비스 보안 체크리스트](recipes/web-security-checklist.md)를 읽고 보안 요구사항을 기본 반영
5. 조합해서 index.html + data.json 생성
6. 로컬에서 테스트
7. 배포 전 보안 체크리스트의 최종 점검표 수행
8. EC2 배포 (`catalog/deploy.md` 따라) — 서버 정보는 사용자에게 요청
9. GitHub 백업
10. 완성 후 → 위의 "1. 새 프로젝트 분석" 워크플로우 실행

### 4. "playbook 전체를 GitHub에 업데이트해줘"

```bash
cd C:\Users\ganna\Downloads\playbook
git add -A
git commit -m "설명"
git push origin main
```

Git 설정:
- user: ganna40
- email: eyeom40@gmail.com
- credential: Git Credential Manager (자동 인증)
- Git 경로: "C:\Program Files\Git\cmd\git.exe"

---

## git-uploader 대시보드

```bash
cd C:\Users\ganna\Downloads\git-uploader
python app.py
# → http://localhost:5000
```

EC2에서 파일 가져와서 GitHub에 올리거나, 로컬 폴더를 GitHub에 올리는 대시보드.

---

## 핵심 규칙

1. **모듈은 독립적이어야 한다** - 각 모듈 파일만 읽으면 복붙 가능해야 함
2. **레퍼런스는 프로필 카드 형태** - 한눈에 뭘 쓰는지 보여야 함
3. **tech-map.md는 항상 최신** - 새 프로젝트 추가 시 반드시 업데이트
4. **코드는 실제 동작하는 것만** - 이론적 설명 아니라 복붙 가능한 코드
5. **한국어로 작성** - 사용자가 한국어 사용자
6. **민감 정보 금지** - 서버 IP, SSH 키, API 키는 `_secrets.md`에만 (gitignore)
7. **새 프로젝트 추가 시 6단계 전부 수행** - 레퍼런스만 만들고 tech-map 안 고치면 안됨
8. **새 기술 = 새 모듈** - 재사용 가능한 새 기술이 보이면 무조건 catalog에 모듈 추가
9. **웹서비스는 보안 체크리스트 기본 적용** - 새 앱 생성/분석/배포 시 `recipes/web-security-checklist.md`를 항상 포함
