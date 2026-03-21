# minpharma - 민파마 제약 기업 웹사이트

> URL: https://minpharma.pearsoninsight.com
> GitHub: https://github.com/ganna40/minpharma

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 기업 웹사이트 + 블로그 CMS |
| **한줄 설명** | 제약 유통사 기업 소개 + 블로그(리치텍스트 에디터) + 관리자 페이지 + 문의 메일 발송 |
| **타겟** | B2B 거래처 (병·의원), 일반 방문자 |
| **테마** | 라이트 (보라+파랑 그라데이션 악센트) |
| **폰트** | Pretendard Variable (시스템 폰트 폴백) |

## 기술 스택

| 구분 | 기술 | 설명 |
|------|------|------|
| **Frontend** | React 19 | CSR SPA, react-router-dom 라우팅 |
| | TypeScript | 전체 프론트엔드 타입 안전 |
| | Vite 8 | 빌드 + HMR + API 프록시 |
| | Tailwind CSS v4 | @theme 기반 디자인 토큰 |
| | TipTap | 리치텍스트 에디터 (Bold/Italic/Heading/Image/Link/파일첨부) |
| | react-router-dom | SPA 라우팅 (/, /blog, /blog/:slug, /admin/*) |
| **Backend** | FastAPI | 비동기 REST API |
| | SQLAlchemy 2.0 async | ORM (aiomysql 드라이버) |
| | python-jose (JWT) | 관리자 인증 (HS256) |
| | aiosmtplib | 비동기 SMTP 메일 발송 (.env 설정) |
| | Uvicorn | ASGI 서버 |
| **Database** | MySQL 8 | 블로그, 제품, 문의 데이터 |
| **Deploy** | EC2 (Ubuntu) | Apache2 리버스 프록시 + systemd |
| | Cloudflare | DNS + SSL |

## 주요 기능

| 기능 | 설명 |
|------|------|
| **기업 랜딩 페이지** | Hero + 회사소개 + 대표이사 + 제품 + 블로그 미리보기 + 문의 (단일 SPA) |
| **블로그 시스템** | 목록(페이지네이션+카테고리필터) + 상세 페이지, API 기반 |
| **리치텍스트 에디터** | TipTap: Bold/Italic/Underline/Heading/정렬/리스트/인용/코드블록/링크/이미지업로드/파일첨부 |
| **관리자 페이지** | JWT 로그인 → 블로그 CRUD (작성/수정/삭제) + 파일 업로드 |
| **이미지/파일 업로드** | POST /api/blog/upload, 10MB 제한, 이미지+문서 지원 |
| **문의 메일 발송** | Contact 폼 → DB 저장 + SMTP 메일 발송 (HTML 템플릿) |
| **스크롤 애니메이션** | fade-section (IntersectionObserver) + 숫자 카운트업 |

## 라우팅 구조

```
/                    → 메인 랜딩 페이지
/blog                → 블로그 목록 (페이지네이션)
/blog/:slug          → 블로그 상세
/admin               → 관리자 로그인
/admin/blog          → 블로그 관리 (목록+삭제)
/admin/blog/new      → 새 글 작성 (리치텍스트)
/admin/blog/edit/:id → 글 수정
```

## API 엔드포인트

```
GET    /api/blog/?page=1&size=10&category=   → 블로그 목록 (페이지네이션)
GET    /api/blog/{slug}                      → 블로그 상세
GET    /api/blog/id/{post_id}                → ID로 조회
POST   /api/blog/                            → 글 작성 (인증)
PUT    /api/blog/{post_id}                   → 글 수정 (인증)
DELETE /api/blog/{post_id}                   → 글 삭제 (인증)
POST   /api/blog/upload                      → 파일 업로드 (인증)
POST   /api/auth/login                       → JWT 로그인
POST   /api/contact/                         → 문의 접수 + 메일 발송
GET    /api/products/                        → 제품 목록
GET    /api/health                           → 헬스체크
```

## DB 스키마

```
blog_posts:     id, title, slug(unique), summary, content(HTML), category, image_url, created_at
contact_inquiries: id, name, email, company, inquiry_type, message, created_at
products:       id, name, slug, description, category, status, is_featured
```

## 프로젝트 구조

```
minpharma/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py        # Settings (DB + SMTP, pydantic-settings)
│   │   │   ├── database.py      # SQLAlchemy async engine
│   │   │   └── email.py         # aiosmtplib 메일 발송
│   │   ├── domains/
│   │   │   ├── auth/            # JWT 로그인 (python-jose)
│   │   │   ├── blog/            # CRUD + 파일 업로드
│   │   │   ├── contact/         # 문의 접수 + 메일
│   │   │   └── products/        # 제품 목록
│   │   └── main.py              # FastAPI 진입점
│   ├── seed.py                  # DB 초기 데이터
│   ├── requirements.txt
│   └── .env.example             # SMTP 설정 템플릿
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx       # 고정 헤더 (react-router 연동)
│   │   │   ├── RichEditor.tsx   # TipTap 리치텍스트 에디터
│   │   │   ├── Hero.tsx         # 히어로 섹션
│   │   │   └── ...              # About, Ceo, Products, Blog, Contact, Footer
│   │   ├── pages/
│   │   │   ├── HomePage.tsx     # 메인 랜딩
│   │   │   ├── BlogListPage.tsx # 블로그 목록 (페이지네이션)
│   │   │   ├── BlogDetailPage.tsx # 블로그 상세 (HTML 렌더링)
│   │   │   ├── AdminLoginPage.tsx # 관리자 로그인
│   │   │   ├── AdminBlogPage.tsx  # 블로그 관리
│   │   │   └── AdminBlogEditPage.tsx # 글 작성/수정
│   │   ├── hooks/               # useScrollFade, useCountUp
│   │   ├── App.tsx              # BrowserRouter + Routes
│   │   └── index.css            # Tailwind @theme + TipTap 스타일
│   ├── package.json
│   └── vite.config.ts           # /api → :8004 프록시
└── .gitignore
```

## 마스터 프롬프트 (AI 복원용)

```
기업 웹사이트 + 블로그 CMS를 만들어줘.

기술 스택:
- Frontend: React 19 + TypeScript + Vite + Tailwind CSS v4 + TipTap 에디터 + react-router-dom
- Backend: FastAPI + SQLAlchemy 2.0 async + aiomysql + python-jose(JWT) + aiosmtplib
- DB: MySQL 8

핵심 기능:
1. 기업 랜딩 페이지 (Hero + 소개 + 제품 + 블로그 미리보기 + 문의)
2. 블로그 시스템 (목록 페이지네이션 + 카테고리 필터 + 상세 페이지)
3. 관리자 로그인 (JWT) → 블로그 CRUD + 리치텍스트 에디터 + 이미지/파일 업로드
4. 문의 폼 → DB 저장 + SMTP 메일 발송
5. Apache2 리버스 프록시 + systemd 서비스로 배포
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 minpharma 레퍼런스를 보고
"[회사명] 기업 웹사이트"를 만들어줘.
React 19 + Vite + Tailwind v4 (프론트)
+ FastAPI + SQLAlchemy async + MySQL (백엔드).
블로그 CMS(TipTap 에디터) + 관리자 JWT 인증 + 문의 메일(SMTP).
```

## 삽질 방지

| 문제 | 원인 | 해결 |
|------|------|------|
| **한글 제목 → slug "untitled"** | `generate_slug`가 ASCII 인코딩으로 한글 전부 제거 | 한글 문자(가-힣) 보존, 빈 결과면 `post-{timestamp}` |
| **수정 시 slug 중복 에러** | PUT endpoint에 slug 중복 체크 없음 | `BlogPost.id != post_id` 조건으로 자기 제외 중복 체크 |
| **pydantic Settings extra fields** | .env에 Settings에 정의 안 된 변수 있으면 에러 | `class Config: extra = "ignore"` |
| **TipTap 수정 모드 빈 에디터** | useEditor가 비동기 fetch 전 빈 content로 초기화 | `fetching` 상태로 에디터 마운트를 데이터 로딩 후로 지연 |
| **Apache + FastAPI SPA** | React Router 경로가 404 반환 | `RewriteRule ^ /index.html [L]` (파일 아닌 요청은 index.html) |
