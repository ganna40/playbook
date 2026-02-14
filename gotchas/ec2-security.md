# EC2 보안 — feroxbuster 차단 + 서버 보안 강화

> 취약점 스캐너(feroxbuster 등)에 의한 서버 다운 방지.
> 실제로 겪고 해결한 사례 (2026.02).
> 원문: https://pearsoninsight.com/feroxbuster-%ea%b3%b5%ea%b2%a9-%ec%b0%a8%eb%8b%a8-ec2-security/

## 증상

- 서버가 하루 2~3번 OOM Kill로 다운
- Cloudflare 방문자는 400명대인데 서버가 죽음
- Apache 로그에 정체불명 IP가 수백 건 요청

## 진단: Apache 로그 분석

```bash
# OOM Kill 발생 시간대 접속 IP 분석
grep "13/Feb/2026:00:0" /var/log/apache2/access.log | \
    awk '{print $1}' | sort | uniq -c | sort -rn | head -5
```

```
199 44.251.91.146    ← 이놈이 범인
  3 ::1
```

```bash
# 해당 IP가 뭘 했는지 확인
grep "44.251.91.146" /var/log/apache2/access.log | head -10
```

```
"GET /wp-admin/.htaccess" 403 "feroxbuster/2.13.0"
"GET /wp-admin/phpMyAdmin" 404 "feroxbuster/2.13.0"
"GET /wp-admin/Pipfile" 404 "feroxbuster/2.13.0"
```

User-Agent: **feroxbuster/2.13.0** — 취약점 스캐너가 576건 요청.

## feroxbuster란

Rust 기반 웹 디렉토리/파일 탐색 도구. 보안 점검용이지만 악의적 사용 많음.
phpMyAdmin, .env, config.php 같은 민감한 파일을 찾아내려고 대량 GET 요청.

### 왜 576건으로 서버가 죽는가

- 존재하지 않는 경로 → WordPress가 PHP로 **144KB짜리 404 페이지** 동적 렌더링
- 576건 × 144KB = ~80MB를 PHP가 처리
- Apache 프로세스가 요청마다 메모리 잡아먹음
- 2GB RAM 바닥 → **OOM Kill → MySQL 사망**

## 대응 1단계: 공격 IP 차단

```bash
# IP 차단
sudo iptables -A INPUT -s 44.251.91.146 -j DROP

# 확인
sudo iptables -L -n | grep 44.251
```

### iptables 영구 저장 (필수!)

```bash
sudo apt install iptables-persistent -y
sudo netfilter-persistent save
```

> **안 하면**: 서버 재부팅 시 차단 규칙 초기화 → 같은 IP 재침입.

## 대응 2단계: 스캐너 User-Agent 일괄 차단

IP는 무한하지만 도구의 UA는 고정. Apache `.htaccess`에서 차단:

```bash
sudo tee -a /var/www/html/.htaccess << 'EOF'

# 취약점 스캐너 UA 차단
RewriteEngine On
RewriteCond %{HTTP_USER_AGENT} (feroxbuster|nikto|sqlmap|dirbuster|gobuster|wfuzz|nuclei) [NC]
RewriteRule .* - [F,L]

EOF
```

| 스캐너 | 정체 |
|--------|------|
| **feroxbuster** | Rust 디렉토리 탐색 (이번 범인) |
| **nikto** | 웹 서버 취약점 스캐너 |
| **sqlmap** | SQL 인젝션 자동화 |
| **dirbuster** | OWASP 디렉토리 브루트포스 |
| **gobuster** | Go 기반 디렉토리 탐색 |
| **wfuzz** | 웹 퍼징 도구 |
| **nuclei** | 템플릿 기반 취약점 스캐너 |

핵심: **PHP 렌더링 없이 Apache에서 바로 403 반환** → 서버 부하 거의 0.

```bash
sudo systemctl restart apache2
```

## 대응 3단계: xmlrpc.php 차단

WordPress의 xmlrpc.php는 브루트포스/DDoS 증폭 공격에 악용됨.

```bash
sudo tee -a /var/www/html/.htaccess << 'EOF'

# xmlrpc.php 차단
<Files xmlrpc.php>
    Require all denied
</Files>

EOF
```

## 대응 4단계: SSL 인증서 적용

```bash
# Let's Encrypt 무료 SSL
sudo certbot --apache -d subdomain.pearsoninsight.com
```

- 자동 Apache 설정 + 90일 자동 갱신
- 모든 서브도메인에 빠짐없이 적용할 것

## 대응 5단계: GA4 추적 코드

Apache 로그만으로는 부족. GA4로 실시간 모니터링.

```html
<!-- index.html의 <head> 바로 뒤에 삽입 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-XXXXXXXXXX');
</script>
```

WordPress는 **Site Kit by Google** 플러그인으로 코드 없이 연동.

## 전체 대응 요약

### 긴급 대응 (1부)

| 순서 | 조치 | 목적 |
|------|------|------|
| 1 | AWS 콘솔에서 인스턴스 중지 후 시작 | 먹통 서버 복구 |
| 2 | Swap 2GB 추가 | OOM Kill 방지 |
| 3 | MySQL 메모리 제한 (128MB) | 메모리 절감 |

### 원인 분석 + 보안 강화 (2부)

| 순서 | 조치 | 목적 |
|------|------|------|
| 4 | Apache 로그로 공격 IP 식별 | 장애 원인 파악 |
| 5 | iptables IP 차단 + 영구 저장 | 재공격 방지 |
| 6 | .htaccess 스캐너 UA 7종 차단 | 도구 기반 일괄 차단 |
| 7 | xmlrpc.php 차단 | WordPress 공격 벡터 제거 |
| 8 | SSL 인증서 적용 | HTTPS 보안 |
| 9 | GA4 추적 코드 삽입 | 트래픽 모니터링 |

## 소규모 EC2 보안 체크리스트

- [ ] Swap 2GB+ 설정
- [ ] MySQL 메모리 제한 (innodb_buffer_pool_size ≤ 128M)
- [ ] iptables-persistent 설치 + 규칙 저장
- [ ] .htaccess 스캐너 UA 차단
- [ ] xmlrpc.php 차단
- [ ] 모든 서브도메인 SSL 인증서
- [ ] GA4 추적 코드
- [ ] Elastic IP 할당
- [ ] Cloudflare Proxy 활성화 (실제 IP 숨김)
- [ ] Apache 디렉토리 리스팅 비활성화
