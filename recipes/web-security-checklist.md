# 웹서비스 보안 체크리스트
> 웹서비스를 만들거나 운영할 때 기본 베이스로 적용하는 보안 점검표.
> 프런트, 백엔드, 관리자 페이지, 서버, Cloudflare, SSL, DB, 로그, 백업까지 한 번에 확인한다.

## 이 문서를 언제 보나

- 새 웹서비스를 설계할 때
- 기존 서비스를 배포하거나 운영 점검할 때
- `/admin`, `/internal`, 결제, 회원정보, 파일 업로드 기능이 있을 때
- 보안 점검 보고서를 만들거나 AI에게 수정 작업을 맡길 때

## 핵심 원칙

| 원칙 | 설명 |
|------|------|
| 비밀값은 서버에만 둔다 | API secret, DB 비밀번호, JWT secret, service role key는 브라우저로 보내지 않는다 |
| 권한 판정은 서버가 한다 | 관리자 여부, 가격, 할인, 결제 성공, 유료 권한은 서버가 최종 확인한다 |
| 관리자 경로는 이중 보호한다 | 프런트 라우트와 서버 API를 둘 다 막아야 한다 |
| 운영 에러는 조용히 처리한다 | 사용자에게는 일반화된 에러만 보여주고 상세 내용은 서버 로그에 남긴다 |
| 인프라 보안도 같이 본다 | Cloudflare, SSL, SSH, 포트, 백업, 모니터링까지 함께 점검한다 |

## 1. 소스 탭 체크

### 확인할 것
- [ ] 브라우저 번들 JS 안에 `SECRET`, `PASSWORD`, `TOKEN`, `DATABASE_URL`, `SMTP`, `PRIVATE_KEY` 같은 문자열이 없다
- [ ] `import.meta.env`, `process.env`, `VITE_*`에 민감값이 들어가지 않는다
- [ ] 관리자 계정명, 내부 URL, 사설 IP, 운영 API 주소가 하드코딩되어 있지 않다
- [ ] source map(`*.js.map`)이 운영에서 공개되지 않는다
- [ ] 관리자 여부를 프런트 하드코딩만으로 판정하지 않는다

### 빠른 명령

```bash
rg -n "VITE_|SECRET|PASSWORD|TOKEN|DATABASE_URL|SMTP|PRIVATE_KEY|ADMIN_" frontend/src frontend/dist
find frontend/dist -name "*.map"
```

### 수정 원칙
- 공개돼도 되는 값만 프런트 환경변수로 둔다
- 비밀값은 서버 `.env` 또는 비밀 저장소에만 둔다
- 운영 빌드에서는 source map을 끈다

## 2. 네트워크 탭 체크

### 확인할 것
- [ ] 관리자 API 요청에 인증이 빠져도 통과하지 않는다
- [ ] 응답 헤더에 보안 헤더가 있다
- [ ] 인증 응답에 `Cache-Control: no-store`가 있다
- [ ] CORS가 `*`로 과하게 열려 있지 않다
- [ ] 쿠키 기반 인증이면 `HttpOnly`, `Secure`, `SameSite`가 붙어 있다
- [ ] 응답 바디에 내부 경로, 스택트레이스, SQL 에러, 테이블명이 노출되지 않는다

### 권장 보안 헤더

| 헤더 | 권장값 예시 |
|------|-------------|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` |
| `Content-Security-Policy` | 서비스에 맞는 최소 권한 정책 |
| `Cache-Control` | 인증/관리자 응답에는 `no-store` |

## 3. 콘솔 탭 체크

### 확인할 것
- [ ] 사용자 브라우저 콘솔에 서버 스택트레이스가 찍히지 않는다
- [ ] DB 테이블명, 파일 경로, 내부 IP, 프레임워크 버전이 에러 메시지에 노출되지 않는다
- [ ] `console.log(token)`, `console.log(user)`, `console.log(paymentResult)` 같은 디버그 로그가 운영에 남아 있지 않다
- [ ] mixed content 에러가 없다

### 수정 원칙
- 사용자에게는 일반화된 에러만 보여준다
- 상세 원인은 서버 로그에만 남긴다
- 운영 빌드에서는 불필요한 디버그 로그를 제거한다

## 4. 관리자 페이지와 권한 체크

### 확인할 것
- [ ] `/admin`, `/internal`은 관리자만 접근 가능하다
- [ ] 로그인하지 않은 사용자는 로그인 페이지로 이동한다
- [ ] 일반 사용자는 관리자 화면에 직접 URL을 쳐도 들어갈 수 없다
- [ ] 프런트에서만 숨기는 게 아니라 서버 API도 같이 막는다
- [ ] 관리자 세션이 만료되면 자동으로 다시 로그인하게 한다
- [ ] 관리자 로그인 경로에는 IP allowlist, VPN, Cloudflare Access 같은 추가 보호를 검토한다

### 최소 기준
- 프런트 보호 라우트 적용
- 백엔드 공통 관리자 의존성 적용
- 운영에서는 관리자 경로에 네트워크 제한 또는 SSO를 붙인다

## 5. 관리자 API 체크

### 확인할 것
- [ ] `/api/admin/*` 또는 관리자 편집 API가 인증 없이 열려 있지 않다
- [ ] 목록 API만 막고 상세 조회 API가 열려 있는 실수가 없다
- [ ] 생성, 수정, 삭제뿐 아니라 편집용 조회 API도 관리자 전용이다
- [ ] 일반 사용자 토큰이나 비로그인 요청은 `401` 또는 `403`을 받는다

### 자주 놓치는 경로
- `GET /api/blog/id/{id}` 같은 편집용 상세 조회
- 파일 업로드 API
- 통계, 대시보드, 관리자 설정 API
- 내부 전용 검색 API

## 6. 인증, 세션, 쿠키 체크

### 확인할 것
- [ ] 로그인 정보는 가능하면 `HttpOnly` 쿠키로 관리한다
- [ ] 세션 또는 토큰 만료 시간이 너무 길지 않다
- [ ] 관리자 계정은 일반 계정보다 더 엄격하게 관리한다
- [ ] 로그인 실패 반복 시 차단하거나 지연시킨다
- [ ] 기본 계정(`admin/admin`, `change-me`)이 없다
- [ ] 운영 비밀값은 코드 기본값이 아니라 환경변수로만 들어간다

### 브라우저 화면 기준 체크 방법

#### Chrome / Edge
1. 개발자도구를 연다
2. `Application` 탭으로 이동한다
3. 왼쪽 `Storage > Cookies > https://도메인`을 선택한다
4. 로그인 후 세션 쿠키를 찾는다
5. 아래 항목을 직접 본다

### 쿠키에서 직접 확인할 항목
- [ ] 쿠키 이름이 세션 목적에 맞게 구분돼 있다
- [ ] `HttpOnly`가 체크되어 있다
- [ ] `Secure`가 체크되어 있다
- [ ] `SameSite`가 `Lax` 또는 `Strict`로 보인다
- [ ] `Expires / Max-Age`가 무한정 길지 않다
- [ ] 관리자 세션 쿠키가 `localStorage` 토큰과 중복 운용되지 않는다

### 해석 기준
- `HttpOnly`: 자바스크립트에서 쿠키를 읽을 수 없다
- `Secure`: HTTPS에서만 전송된다
- `SameSite=Lax`: 대부분 기본 폼 이동에 안전한 편이다
- `SameSite=Strict`: 더 엄격하지만 외부 링크 흐름과 충돌할 수 있다
- 관리자 세션은 가능하면 `HttpOnly + Secure + SameSite=Lax/Strict` 조합을 쓴다

## 7. 결제, 가격, 권한부여 체크

### 확인할 것
- [ ] 가격, 할인, 플랜 변경은 서버가 최종 확인한다
- [ ] 프런트가 보낸 금액을 그대로 믿지 않는다
- [ ] 결제 성공 여부를 서버에서 다시 검증한다
- [ ] 결제 후 권한 부여도 서버에서 처리한다
- [ ] 사용자가 요청 값을 바꿔서 프리미엄 권한을 얻을 수 없다

### 원칙
- 프런트는 표시만 한다
- 서버가 가격 계산, 결제 검증, 권한 반영을 모두 맡는다

## 8. DB / Supabase 체크

### 공통
- [ ] DB는 외부에 직접 공개하지 않는다
- [ ] 앱용 계정과 관리자 계정을 분리한다
- [ ] 민감 데이터는 최소 권한으로만 접근한다
- [ ] 읽기 전용 계정과 쓰기 계정을 분리할 수 있으면 분리한다

### PostgreSQL
- [ ] 민감 테이블에 RLS를 켰다
- [ ] `SELECT`, `INSERT`, `UPDATE`, `DELETE` 정책이 모두 있다
- [ ] 사용자가 자기 데이터만 읽고 쓰게 `user_id = auth.uid()` 같은 정책을 넣었다
- [ ] 관리자 전체 조회는 별도 정책 또는 별도 role로만 허용한다
- [ ] View, Function, Materialized View가 RLS 우회 경로가 되지 않는다

### MariaDB / MySQL
- [ ] 모든 민감 조회 API에 `WHERE owner_id = current_user_id` 같은 조건이 강제된다
- [ ] 목록뿐 아니라 상세 조회, 수정, 삭제에도 owner 조건이 들어간다
- [ ] `get(id)` 같은 단순 조회가 그대로 쓰이지 않는다
- [ ] 서버 코드에서 권한 필터를 빠뜨린 API가 없다

### Supabase
- [ ] 민감 테이블에 RLS를 켰다
- [ ] `anon`으로 열려 있으면 안 되는 테이블이 공개되지 않는다
- [ ] 사용자가 자기 데이터만 읽고 쓰게 정책이 있다
- [ ] `service_role` 키가 클라이언트에 노출되지 않는다
- [ ] Storage, RPC, Edge Function도 같은 기준으로 점검한다

## 9. Cloudflare / SSL 체크

### 확인할 것
- [ ] DNS가 Cloudflare 프록시(주황 구름)로 켜져 있다
- [ ] SSL/TLS 모드가 `Full (Strict)`다
- [ ] `Always Use HTTPS`가 켜져 있다
- [ ] `Automatic HTTPS Rewrites`가 켜져 있다
- [ ] `http://도메인`으로 접근하면 `https://도메인`으로 리다이렉트된다
- [ ] 브라우저 주소창에 자물쇠 표시가 뜬다
- [ ] 콘솔에 mixed content 에러가 없다

## 10. 서버 인증서 / Nginx 또는 Apache 체크

### 확인할 것
- [ ] 서버에 SSL 인증서가 설치되어 있다
- [ ] 웹서버가 443 포트 HTTPS로 정상 응답한다
- [ ] 80 포트는 HTTPS로 리다이렉트된다
- [ ] 인증서 만료일을 확인했다
- [ ] 인증서 경로가 웹서버 설정에 정확히 연결되어 있다
- [ ] `Full (Strict)` 사용 시 원본 서버 인증서가 유효하다

### 빠른 명령

```bash
curl -I http://example.com
curl -I https://example.com
openssl s_client -connect example.com:443 -servername example.com
```

## 11. 서버 접속 보안 체크

### 확인할 것
- [ ] SSH 비밀번호 로그인을 껐다
- [ ] SSH 키 로그인만 허용했다
- [ ] `root` 직접 로그인을 막았다
- [ ] SSH 접근 가능한 IP를 제한했다
- [ ] 서버 관리자 계정에 MFA를 적용할 수 있으면 적용했다

### 권장 기준
- `PasswordAuthentication no`
- `PermitRootLogin no`
- 운영 점프 호스트, VPN, Cloudflare Tunnel, Bastion 중 하나 사용

## 12. 방화벽 / 포트 체크

### 확인할 것
- [ ] 외부에 꼭 필요한 포트만 열었다
- [ ] 보통 80, 443만 열고 나머지는 닫았다
- [ ] SSH 포트는 꼭 필요할 때만 열었다
- [ ] DB 포트(예: 5432, 3306)를 외부에 공개하지 않았다
- [ ] 사용하지 않는 서비스와 포트를 정리했다

### 빠른 명령

```bash
ss -tulpn
sudo ufw status
```

## 13. 환경변수 / 비밀정보 체크

### 확인할 것
- [ ] `.env` 파일이 외부에 노출되지 않는다
- [ ] GitHub 등에 비밀키를 올리지 않았다
- [ ] API secret, DB 비밀번호, Stripe secret, Supabase service role key를 클라이언트에 넣지 않았다
- [ ] 프런트 코드에서 비밀키가 보이지 않는다
- [ ] 배포 환경변수 권한을 최소한으로 관리한다

## 14. 에러 / 로그 체크

### 확인할 것
- [ ] 사용자에게 상세 에러를 보여주지 않는다
- [ ] 스택트레이스, 내부 파일 경로, DB 테이블명 노출이 없다
- [ ] 상세 에러는 서버 로그에만 남긴다
- [ ] 로그인 실패 로그를 남긴다
- [ ] 관리자 접근 로그를 남긴다
- [ ] 로그에 비밀번호, 토큰 같은 민감정보를 남기지 않는다

## 15. 업로드 / 파일 보안 체크

### 확인할 것
- [ ] 업로드 가능한 파일 형식을 제한했다
- [ ] 실행파일 업로드를 차단했다
- [ ] 업로드 파일 이름을 검증한다
- [ ] 업로드 폴더에 위험한 실행 권한이 없다
- [ ] 악성 파일 업로드 가능성을 점검했다

## 16. 백업 / 복구 / 모니터링 체크

### 확인할 것
- [ ] DB 자동 백업이 있다
- [ ] 파일 백업이 있다
- [ ] 백업 복구 테스트를 해봤다
- [ ] 서버 다운이나 에러 급증 알림이 온다
- [ ] CPU, 메모리, 디스크 사용량을 모니터링한다
- [ ] 이상 트래픽이 생기면 확인할 수 있다

## 배포 전 최종 체크

- [ ] 운영 `.env`에 실제 비밀값이 들어 있다
- [ ] 기본 계정, 기본 secret, 샘플 키가 제거됐다
- [ ] source map이 비활성화되었다
- [ ] 관리자 페이지와 관리자 API를 둘 다 점검했다
- [ ] 인증 실패, 권한 부족, 비로그인 상태를 각각 테스트했다
- [ ] 보안 헤더와 쿠키 플래그를 브라우저에서 직접 확인했다
- [ ] SSL 리다이렉트와 자물쇠 표시를 확인했다
- [ ] 백업과 복구 경로를 확인했다

## AI에게 바로 맡기는 프롬프트

```text
이 프로젝트에서 웹서비스 보안 점검과 수정 작업을 해줘.

점검 범위:
- 소스 탭: 클라이언트 번들에 secret, token, 내부 URL, admin 관련 하드코딩 값 노출 여부
- 네트워크 탭: 인증 누락, 민감정보 노출, CORS, 쿠키, 보안 헤더
- 콘솔 탭: 스택트레이스, 내부 경로, DB 정보 노출 여부
- /admin, /internal 페이지 접근 제어
- 관리자 API 인증 및 권한 검사
- 결제, 가격, 권한 검증의 서버 처리 여부
- DB 권한 정책, PostgreSQL RLS 또는 MySQL/MariaDB owner 필터
- Cloudflare, SSL, SSH, 포트, 백업, 모니터링

수정 원칙:
- 관리자 페이지와 관리자 API를 둘 다 막아라
- 환경변수와 secret은 클라이언트에 절대 노출하지 마라
- 프로덕션에서는 상세 에러를 숨기고 서버 로그에만 남겨라
- HttpOnly, Secure, SameSite 쿠키를 우선 검토하라
- 기존 기능을 최대한 안 깨는 최소 수정부터 적용하라

결과물:
- 취약점 목록
- 심각도
- 수정한 파일 목록
- 변경 이유
- 직접 테스트할 체크리스트
```

## 함께 보면 좋은 문서

- [minpharma](../references/minpharma.md)
- [FastAPI+SQLAlchemy async](fastapi-sqlalchemy-async.md)
- [EC2 보안 (feroxbuster 차단)](../gotchas/ec2-security.md)
- [Cloudflare + Apache 배포](../gotchas/cloudflare-apache.md)
