# WordPress Domain + SSL - Cloudflare + EC2 도메인 연결

> 도메인 구매 → Cloudflare DNS → SSL 자동 적용 → WordPress 주소 변경 → DB 일괄 수정.
> [AWS WordPress 설치](recipes/aws-wordpress.md) 완료 후 진행.
> 원문: https://pearsoninsight.com/워드프레스-도메인-연결/

## 도메인 구매

Cloudflare 추천 — 원가(도매가) 판매, 갱신 비용도 동일.

| 업체 | .com 연간 | 특징 |
|------|-----------|------|
| **Cloudflare** | ~$10 (≈13,000원) | **원가 판매**, 갱신도 동일 가격 |
| Namecheap | ~$10~13 | 첫 해 할인, UI 편리 |
| Porkbun | ~$10 | 저렴 + 무료 WHOIS 보호 |
| 가비아 | ~16,500원 | 국내 1위, 한국어 지원 |

> 수익형 블로그는 **.com** 추천. .org는 비영리 단체용이라 블로그에 안 어울림.

## 1단계: Cloudflare DNS 설정

Cloudflare 대시보드 → 도메인 클릭 → DNS → Records → Add record.

| 타입 | 이름 | 값 | 프록시 |
|------|------|-----|--------|
| A | `@` | EC2 퍼블릭 IP | **프록시됨** (주황색 구름) |
| A | `www` | EC2 퍼블릭 IP | **프록시됨** (주황색 구름) |

> EC2 퍼블릭 IP: AWS 콘솔 → EC2 → 인스턴스 클릭 → 퍼블릭 IPv4 주소.
> **프록시(주황색 구름) 반드시 켜기** — Cloudflare가 SSL 인증서를 자동 제공.
> 반영 시간: Cloudflare는 보통 5분 이내.

## 2단계: SSL(HTTPS) 설정

Cloudflare 프록시를 켜면 서버에 Certbot/Let's Encrypt 설치 없이 SSL 자동 적용.

### SSL 모드 선택

Cloudflare → SSL/TLS → 모드 선택:

| 모드 | 설명 | 추천 |
|------|------|------|
| **Flexible** | 서버에 SSL 설치 불필요 | **블로그 용도 추천** |
| Full | 서버에 자체 서명 인증서 필요 | |
| Full (Strict) | 서버에 정식 SSL 필요 | 가장 안전 |

### Edge Certificates 필수 설정

SSL/TLS → Edge Certificates에서 **둘 다 켜기**:

| 설정 | 역할 |
|------|------|
| **Always Use HTTPS** | HTTP → HTTPS 자동 리다이렉트 |
| **Automatic HTTPS Rewrites** | 페이지 내 HTTP 리소스를 HTTPS로 변환 |

> ⚠️ Automatic HTTPS Rewrites 안 켜면 나중에 Mixed Content로 사이트 깨짐.

## 3단계: WordPress 주소 변경

워드프레스 관리자 → 설정 → 일반:

| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| WordPress 주소(URL) | `http://EC2퍼블릭IP` | `https://내도메인.com` |
| 사이트 주소(URL) | `http://EC2퍼블릭IP` | `https://내도메인.com` |

변경사항 저장 → 로그인 풀림 → `https://내도메인.com/wp-admin`으로 재로그인.

## 4단계: WP-CLI로 DB 일괄 변환

DB에 저장된 이미지/CSS/콘텐츠 경로가 `http://이전IP`로 남아있으면 사이트가 깨짐. WP-CLI로 일괄 수정.

### WP-CLI 설치

```bash
# 반드시 홈 디렉토리에서 실행 (/var/www/html에서 하면 Permission denied)
cd ~
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
sudo mv wp-cli.phar /usr/local/bin/wp

# 설치 확인
wp --version
```

### DB 일괄 변환

```bash
cd /var/www/html

# 이전 IP → 새 도메인으로 변환
wp search-replace 'http://EC2퍼블릭IP' 'https://내도메인.com' --all-tables --allow-root

# http → https 변환도 함께
wp search-replace 'http://내도메인.com' 'https://내도메인.com' --all-tables --allow-root
```

`Made X replacements` 메시지 나오면 성공. `Ctrl+Shift+R` (강력 새로고침)으로 확인.

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| 관리자 페이지 접속 불가 | DNS 미반영 상태에서 주소 변경 | `wp-config.php` 수정 (아래) |
| CSS/디자인 깨짐 | Mixed Content (HTTP 리소스 차단) | Automatic HTTPS Rewrites 확인 + WP-CLI |
| 로고/이미지 깨짐 | DB에 이전 IP 경로 남아있음 | WP-CLI `search-replace` |
| 플러그인으로도 안 잡힘 | DB에 하드코딩된 URL | WP-CLI가 가장 확실 |

### 관리자 접속 불가 시 복구

```bash
ssh -i "키파일.pem" ubuntu@EC2퍼블릭IP

sudo nano /var/www/html/wp-config.php
```

`/* That's all, stop editing! */` 줄 **위에** 추가:

```php
define('WP_HOME', 'https://내도메인.com');
define('WP_SITEURL', 'https://내도메인.com');
```

```bash
sudo systemctl restart apache2
```

> 정상 접속 확인 후 추가한 두 줄은 삭제해도 됨.

### Mixed Content가 계속될 때

Cloudflare + WP-CLI로도 안 되면 **Really Simple SSL** 플러그인 설치:

플러그인 → 새로 추가 → "Really Simple SSL" 검색 → 설치 → 활성화.

## 전체 체크리스트

| 순서 | 작업 | 위치 |
|------|------|------|
| 1 | 도메인 구매 (.com) | Cloudflare |
| 2 | DNS A 레코드 추가 (@ + www → EC2 IP) | Cloudflare DNS |
| 3 | 프록시(주황색 구름) 켜기 | Cloudflare DNS |
| 4 | SSL 모드 → Flexible | Cloudflare SSL/TLS |
| 5 | Always Use HTTPS + Automatic HTTPS Rewrites 켜기 | Cloudflare Edge Certificates |
| 6 | WordPress 주소/사이트 주소를 `https://도메인`으로 변경 | WordPress 설정 → 일반 |
| 7 | 관리자 접속 안 되면 `wp-config.php` 수정 | SSH |
| 8 | WP-CLI 설치 → DB 일괄 변환 (IP→도메인, http→https) | SSH |
| 9 | 사이트 깨짐 확인 → Really Simple SSL 설치 (필요 시) | WordPress 플러그인 |

## 주의사항

- 도메인 구매 시 **첫 해 할인**에 속지 말 것 — 갱신 가격 확인 필수
- DNS A 레코드의 **프록시(주황색 구름)** 안 켜면 SSL 자동 적용 안 됨
- WordPress 주소 변경은 **DNS 반영 확인 후** 진행 — 안 그러면 관리자 접속 불가
- WP-CLI `curl -O`는 반드시 **`cd ~`** 후 실행 — `/var/www/html`에서 하면 Permission denied
- `wp search-replace`는 **`--allow-root`** 필수 (Ubuntu 기본 사용자가 root 권한)

## AI 프롬프트 예시

```
EC2 WordPress에 도메인을 연결해줘.
- Cloudflare DNS A 레코드 설정 (프록시 켜기)
- SSL 모드 Flexible + Always Use HTTPS + Automatic HTTPS Rewrites
- WordPress 주소를 https://내도메인.com으로 변경
- WP-CLI 설치 후 DB 일괄 변환 (이전 IP → 새 도메인)
- 위 레시피 순서대로 진행
```
