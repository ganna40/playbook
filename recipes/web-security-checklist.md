# 웹서비스 보안 체크리스트

> 새 홈페이지, 랜딩페이지, SaaS, 관리자 페이지를 만들고 배포할 때 쓰는 실전 점검표.
> **기획 → 개발 → 배포 → 운영** 순서로 한 번씩 훑으면 된다.

## 언제 쓰나

- 새 웹서비스를 처음 만들 때
- 관리자 페이지(`/admin`)나 내부 페이지(`/internal`)가 있을 때
- 결제, 포인트, 가격, 권한, 개인정보를 다룰 때
- 배포 직전 최종 점검이 필요할 때
- 개발자도구에서 코드/헤더/에러가 많이 보여서 불안할 때

## 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **비밀은 서버에만** | API 키, DB URL, JWT secret, SMTP 비밀번호는 브라우저로 보내지 않는다 |
| **권한은 서버가 판단** | admin 여부, 가격, 할인, 결제 성공 여부를 프론트가 결정하면 안 된다 |
| **실패는 조용히, 기록은 서버에** | 사용자에게는 일반화된 오류만, 상세 원인은 서버 로그에 남긴다 |
| **관리자 경로는 2중 보호** | 프런트 라우트 가드 + 서버 API 권한 검사 둘 다 필요 |
| **기본값 금지** | `admin/admin`, `change-me`, `dev-only-secret` 같은 값으로 운영하지 않는다 |

## 1. 소스 탭 체크

### 확인할 것

- [ ] 번들 JS 안에 `SECRET`, `PASSWORD`, `TOKEN`, `DATABASE_URL`, `SMTP`, `PRIVATE_KEY` 같은 문자열이 없는가
- [ ] `import.meta.env`, `process.env`, `VITE_*` 변수가 민감값을 포함하지 않는가
- [ ] 관리자 계정명, 내부 API 경로, 사설 도메인, 개발용 서버 주소가 하드코딩되지 않았는가
- [ ] source map(`*.js.map`)이 운영에서 공개되지 않는가
- [ ] 관리자 권한 판정이 프런트 하드코딩(`if (role === 'admin')`)에만 의존하지 않는가

### 빠른 점검 명령

```bash
rg -n "VITE_|SECRET|PASSWORD|TOKEN|DATABASE_URL|SMTP|PRIVATE_KEY|ADMIN_" frontend/src frontend/dist
find frontend/dist -name "*.map"
```

### 수정 원칙

- 공개돼도 되는 값만 `VITE_*`로 둔다
- 민감값은 무조건 백엔드 `.env`
- 운영 빌드에서 source map 비활성화

```ts
// vite.config.ts
export default defineConfig({
  build: {
    sourcemap: false,
  },
})
```

## 2. 네트워크 탭 체크

### 확인할 것

- [ ] 관리자 API 요청에 인증 헤더나 세션 쿠키가 반드시 필요한가
- [ ] 응답 헤더에 보안 헤더가 있는가
- [ ] 인증 관련 응답에 `Cache-Control: no-store`가 있는가
- [ ] CORS가 `*`로 열려 있지 않은가
- [ ] 쿠키를 쓰면 `HttpOnly`, `Secure`, `SameSite`가 설정되어 있는가
- [ ] 응답 바디에 내부 경로, 스택트레이스, SQL 에러, 테이블명이 노출되지 않는가

### 권장 보안 헤더

| 헤더 | 권장값 예시 |
|------|-------------|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` |
| `Content-Security-Policy` | 서비스에 맞는 최소 권한 정책 |
| `Cache-Control` | 인증/관리자 응답은 `no-store` |

### FastAPI 예시

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith("/api/auth/"):
        response.headers["Cache-Control"] = "no-store"
    return response
```

## 3. 콘솔 탭 체크

### 확인할 것

- [ ] 사용자 브라우저 콘솔에 서버 스택트레이스가 그대로 뜨지 않는가
- [ ] DB 테이블명, 파일 시스템 경로, 내부 IP, 프레임워크 버전이 에러 메시지에 실리지 않는가
- [ ] `console.log(token)`, `console.log(user)`, `console.log(paymentResult)` 같은 디버그 로그가 남아 있지 않은가

### 수정 원칙

- 사용자 메시지는 일반화
- 상세 원인은 서버 로그로
- 프런트 디버그 로그는 운영에서 제거

```python
@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled application error")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
```

## 4. 관리자 페이지 체크

### 확인할 것

- [ ] `/admin`, `/internal` 페이지는 비로그인 사용자가 직접 URL 입력해도 접근 불가인가
- [ ] 프런트에서만 막는 것이 아니라 서버 API도 별도로 막는가
- [ ] 관리자 세션/토큰 만료 시 자동 로그아웃되는가
- [ ] 관리자 IP allowlist 또는 VPN/Cloudflare Access가 있는가

### 최소 기준

- 프런트: 보호 라우트
- 백엔드: `get_current_admin()` 같은 공통 의존성
- 운영: IP allowlist 또는 SSO/Access

```tsx
<Route
  path="/admin/blog"
  element={<ProtectedRoute><AdminBlogPage /></ProtectedRoute>}
/>
```

```python
@router.post("/admin-only")
async def admin_only_route(admin: dict = Depends(get_current_admin)):
    ...
```

## 5. 관리자 API 체크

### 확인할 것

- [ ] `/api/admin/*` 또는 관리자 편집용 API가 인증 없이 열려 있지 않은가
- [ ] 목록 API만 막고 상세 조회 API는 열려 있는 실수가 없는가
- [ ] create/update/delete 외에 edit용 read API도 관리자 전용인가
- [ ] 일반 사용자 토큰으로 관리자 API를 호출해도 403/401이 나는가

### 자주 놓치는 경로

- `GET /api/blog/id/{id}` 같은 편집용 상세 조회
- 업로드 엔드포인트
- 통계/대시보드 API
- 내부 설정 조회 API

## 6. 가격/결제/권한 검증 체크

### 확인할 것

- [ ] 가격 계산을 프런트 값 그대로 신뢰하지 않는가
- [ ] 할인율, 최종 금액, 결제 성공 여부를 서버가 재검증하는가
- [ ] 권한 승격(`premium`, `admin`, `paid`)이 프런트 상태만으로 결정되지 않는가

### 원칙

- 프런트는 표시만
- 서버가 최종 계산/검증
- 결제 웹훅 또는 PG 검증 응답으로 상태 확정

## 7. 인증/세션 체크

### 확인할 것

- [ ] 운영에서 기본 자격증명(`admin`, `change-me`)을 사용하지 않는가
- [ ] 로그인 실패 제한이 있는가
- [ ] 관리자 로그인에 네트워크 제한 또는 2FA가 있는가
- [ ] 토큰 만료시간이 너무 길지 않은가
- [ ] 가능하면 `localStorage` 대신 `HttpOnly` 쿠키를 사용하는가

### 최소 기준

- IP당 5회 실패 → 15분 차단
- 감사 로그 기록
- 운영 비밀값은 `.env`에서만 주입

## 8. CORS/쿠키 체크

### 확인할 것

- [ ] `allow_origins=["*"]` + 인증 조합을 쓰지 않는가
- [ ] 실제 프런트 도메인만 허용하는가
- [ ] 쿠키 기반 인증이면 `allow_credentials=True`와 정확한 origin allowlist를 쓰는가

### 예시

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://example.com",
        "https://admin.example.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## 9. DB 종류별 체크

### PostgreSQL을 쓸 때

- [ ] 사용자별 민감 테이블에 RLS(Row Level Security)를 켰는가
- [ ] `SELECT`, `UPDATE`, `DELETE`, `INSERT` 정책이 모두 있는가
- [ ] 사용자 본인 데이터만 읽도록 `user_id = auth.uid()` 또는 동등한 조건이 있는가
- [ ] 관리자만 전체 조회 가능한 별도 정책이 있는가
- [ ] View, Function, Materialized View가 RLS 우회 경로가 되지 않는가

### PostgreSQL 권장 원칙

- 새 민감 테이블 생성 시: **테이블 생성 → RLS 활성화 → 정책 작성** 순서로 간다
- 앱 코드에서 한 번 막고, DB 정책에서 한 번 더 막는다
- 관리자 조회는 별도 role 또는 명시적 정책으로만 허용한다

### PostgreSQL 정책 예시

```sql
alter table orders enable row level security;

create policy "users_can_read_own_orders"
on orders
for select
using (user_id = auth.uid());

create policy "users_can_update_own_orders"
on orders
for update
using (user_id = auth.uid());
```

### MariaDB / MySQL을 쓸 때

- [ ] 민감 데이터 조회 API에 `WHERE owner_id = current_user_id` 조건이 빠지지 않았는가
- [ ] 목록 API뿐 아니라 상세 조회/수정/삭제에도 owner 조건이 들어가는가
- [ ] 관리자 전용 API와 일반 사용자 API가 분리되어 있는가
- [ ] DB 계정 권한이 과도하지 않은가
- [ ] 가능하면 읽기 전용 계정과 쓰기 계정을 분리했는가

### MariaDB / MySQL 주의

- PostgreSQL식 RLS가 없으므로 **앱 코드에서 강제**해야 한다
- 쿼리 한 군데라도 owner 조건이 빠지면 그대로 데이터 유출이 된다
- ORM을 쓰더라도 `get(id)` 같은 단순 조회는 매우 위험하므로 `where(id=?, owner_id=?)` 형태로 강제한다

### MariaDB / MySQL 예시

```python
result = await db.execute(
    select(Order).where(
        Order.id == order_id,
        Order.user_id == current_user.id,
    )
)
order = result.scalar_one_or_none()
```

## 10. Supabase / PostgreSQL 체크

### Supabase를 쓸 때

- [ ] 테이블별 RLS가 켜져 있는가
- [ ] `anon` 키로 읽히면 안 되는 테이블이 공개되지 않았는가
- [ ] `auth.uid()` 기준 본인 데이터만 읽도록 정책이 있는가
- [ ] admin/service_role 키가 프런트에 들어가지 않았는가
- [ ] Edge Function, RPC, Storage 정책도 같은 기준으로 막혀 있는가

### 주의

- `service_role`은 절대 클라이언트 금지
- RLS 없는 테이블은 사실상 공개 가능성으로 간주
- Supabase도 본질적으로 PostgreSQL이므로, 민감 테이블이면 RLS를 기본값으로 본다

## 11. 운영 전 최종 점검표

- [ ] 운영 `.env`에 실제 비밀값 설정
- [ ] source map 비활성화 또는 비공개 처리
- [ ] 관리자 경로/관리자 API 차단 테스트
- [ ] 잘못된 토큰/없는 토큰/일반 사용자 토큰으로 모두 테스트
- [ ] 응답 헤더 확인
- [ ] 상세 에러 노출 확인
- [ ] rate limit 확인
- [ ] 로그에 감사 이벤트 남는지 확인
- [ ] 백업/롤백 경로 확보

## 직접 테스트 명령 예시

```bash
# 관리자 상세 API 비인증 접근 차단 확인
curl -i https://example.com/api/blog/id/1

# 인증 응답 캐시 금지 확인
curl -i https://example.com/api/auth/me

# source map 공개 여부 확인
curl -i https://example.com/assets/index-xxxx.js.map

# 보안 헤더 확인
curl -I https://example.com/api/health
```

## DB별 한 줄 요약

| DB | 핵심 원칙 |
|----|-----------|
| PostgreSQL | 가능하면 RLS를 기본값으로 켠다 |
| Supabase | `service_role`은 서버 전용, RLS 없는 테이블은 위험으로 본다 |
| MariaDB / MySQL | RLS가 없으니 앱 코드에서 owner 필터를 강제한다 |

## AI에게 시킬 때 프롬프트

```text
이 프로젝트에서 웹서비스 보안 점검을 해줘.

점검 범위:
- 소스 탭: 번들에 secret, token, 내부 URL 노출 여부
- 네트워크 탭: 인증 누락, CORS, 쿠키, 보안 헤더
- 콘솔 탭: 상세 에러/스택트레이스 노출 여부
- /admin, /internal 페이지 접근 제어
- 관리자 API 인증/권한 검사
- 결제/가격/권한 서버 검증 여부
- Supabase 사용 시 RLS 정책 여부

수정 원칙:
- 최소 수정 우선
- 관리자 페이지와 관리자 API 모두 차단
- 프로덕션 상세 에러 숨김
- 환경변수/비밀은 클라이언트 금지
- 마지막에 취약점 목록 + 수정 파일 + 테스트 체크리스트 보고서 작성
```

## 레퍼런스

- [minpharma](references/minpharma.md) — 기업 웹사이트에서 관리자 보호, 보안 헤더, 에러 숨김, rate limit 적용 사례
- [FastAPI+SQLAlchemy async](recipes/fastapi-sqlalchemy-async.md) — FastAPI 백엔드 기본 구조
- [EC2 보안 (feroxbuster 차단)](gotchas/ec2-security.md) — 운영 서버 보안 점검 포인트
