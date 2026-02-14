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

## 폴더 구조

```
playbook/
├── index.html          # Docsify 설정 (건드리지 마)
├── _sidebar.md         # 사이드바 네비게이션
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
│   └── deploy.md       # EC2 배포
│
├── references/         # 실제 만든 앱 분석
│   ├── README.md       # 레퍼런스 목록
│   ├── salary.md       # 월급계산기
│   ├── pong.md         # 퐁퐁측정기
│   ├── mz.md           # MZ력측정기
│   └── amlife.md       # 엠생력측정기
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

**순서:**

1. 프로젝트 코드를 읽는다 (index.html, data.json 등)
2. 사용된 기술을 카테고리별로 분류한다:
   - 프론트엔드 (CSS 방식, 폰트, 차트 등)
   - API/SDK (카카오, GA, 외부 서비스)
   - 서버/인프라 (호스팅, DNS, SSL)
   - 데이터 (JSON 구조, 로드 방식)
3. 기존 모듈과 비교한다:
   - 기존 모듈로 설명 가능 → 레퍼런스만 추가
   - 새로운 패턴 발견 → 새 모듈 파일 생성
4. 아래 파일들을 업데이트한다:

| 파일 | 할 일 |
|------|-------|
| `references/새프로젝트.md` | 새로 생성 (아래 템플릿 따라) |
| `references/README.md` | 목록에 추가 |
| `tech-map.md` | 기술 카테고리 + 매트릭스 + 프로필 카드 추가 |
| `catalog/README.md` | 새 모듈 있으면 추가 |
| `catalog/새모듈.md` | 새 모듈 있으면 생성 |
| `_sidebar.md` | 네비게이션에 추가 |

5. git commit + push

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
4. 조합해서 index.html + data.json 생성
5. 로컬에서 테스트
6. EC2 배포 (`catalog/deploy.md` 따라)
7. GitHub 백업
8. 완성 후 → references에 새 레퍼런스로 추가

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

## 서버 정보

| 항목 | 값 |
|------|-----|
| EC2 IP | 3.34.190.131 |
| SSH User | ubuntu |
| SSH Key | C:\Users\ganna\Downloads\eyeom40.pem |
| Web Root | /var/www/ |
| Nginx 설정 | /etc/nginx/sites-available/ |
| Domain | *.pearsoninsight.com (Cloudflare) |
| GitHub | ganna40 |
| GA ID | G-QL0VH60WTE |

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
