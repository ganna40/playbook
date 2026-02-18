# Cloudflare + Apache 삽질 방지

> Cloudflare 프록시 + Apache2로 서브도메인 배포할 때 자주 겪는 함정들.
> 실제 사례: poli.pearsoninsight.com 배포 (2026.02)

---

## 1. ERR_TOO_MANY_REDIRECTS (리다이렉트 루프)

### 증상

배포 직후 브라우저에 `ERR_TOO_MANY_REDIRECTS`. 시크릿 모드에서도 동일.

### 원인

Cloudflare SSL 모드가 **Flexible**이면:

```
브라우저 → Cloudflare (HTTPS) → Apache (HTTP)
```

Apache에서 `certbot --redirect`를 쓰면 Apache가 HTTP를 HTTPS로 리다이렉트.
Cloudflare가 이미 HTTPS → HTTP로 변환했는데 Apache가 다시 HTTP → HTTPS로 돌려보냄.

```
브라우저 → Cloudflare HTTPS → Apache HTTP → Apache redirect HTTPS
→ Cloudflare HTTPS → Apache HTTP → Apache redirect HTTPS → 무한루프
```

### 해결

Apache VirtualHost(`/etc/apache2/sites-available/poli.conf`)에서 certbot이 추가한 `RewriteRule` 제거:

```apache
# 이 블록 전체 제거
# RewriteEngine on
# RewriteCond %{SERVER_NAME} =poli.pearsoninsight.com
# RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
```

HTTP→HTTPS 리다이렉트는 Cloudflare에 맡김.
Cloudflare SSL 모드를 **Full** 또는 **Full (Strict)**로 바꾸면 certbot redirect를 써도 되지만, Flexible 모드에선 Apache 리다이렉트를 끄는 게 가장 빠름.

```bash
sudo systemctl reload apache2
```

---

## 2. Apache ProxyPass 부분 누락 → fetch 실패 ("—" 표시)

### 증상

`/visit`은 정상인데 `/count`만 fetch하면 404 또는 응답 없음. 프론트에서 `"—"` 표시.

### 원인

ProxyPass를 엔드포인트 별로 하나씩 추가해야 하는데 일부를 빠뜨린 경우.

### 해결

HTTP VirtualHost와 HTTPS VirtualHost 둘 다에 모든 엔드포인트 추가:

```apache
# /etc/apache2/sites-available/poli.conf (HTTP)
ProxyPass /visit http://127.0.0.1:8002/visit
ProxyPassReverse /visit http://127.0.0.1:8002/visit
ProxyPass /count http://127.0.0.1:8002/count
ProxyPassReverse /count http://127.0.0.1:8002/count
```

```apache
# /etc/apache2/sites-available/poli-le-ssl.conf (HTTPS, certbot 생성)
ProxyPass /visit http://127.0.0.1:8002/visit
ProxyPassReverse /visit http://127.0.0.1:8002/visit
ProxyPass /count http://127.0.0.1:8002/count
ProxyPassReverse /count http://127.0.0.1:8002/count
```

```bash
sudo systemctl reload apache2
```

> **체크 포인트**: 엔드포인트 추가할 때마다 HTTP + HTTPS 두 파일 모두 편집했는지 확인.

---

## 3. Cloudflare 프록시 환경에서 실제 클라이언트 IP

### 증상

`request.environ.get('REMOTE_ADDR')`가 항상 Cloudflare 엣지 IP (`103.x.x.x`)를 반환.
모든 방문자가 같은 IP로 집계되어 중복 제거 불가.

### 원인

Cloudflare가 프록시로 동작하면 실제 클라이언트 IP는 `CF-Connecting-IP` 헤더에 담김.
서버 입장에서 요청 출처는 Cloudflare 엣지 노드.

### 해결

Python http.server 기반 카운터에서 `CF-Connecting-IP` 헤더를 우선 사용:

```python
def get_client_ip(self):
    # Cloudflare 프록시 환경: 실제 IP는 CF-Connecting-IP 헤더
    cf_ip = self.headers.get('CF-Connecting-IP')
    if cf_ip:
        return cf_ip.strip()
    # fallback: 직접 접속 또는 로컬 테스트
    return self.client_address[0]
```

IP를 그대로 저장하지 않고 SHA256 해시로 저장 (개인정보 보호):

```python
import hashlib
ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()
```

SQLite에서 해시로 중복 제거:

```sql
CREATE TABLE IF NOT EXISTS visits (ip_hash TEXT PRIMARY KEY);
INSERT OR IGNORE INTO visits (ip_hash) VALUES (?);
SELECT COUNT(*) FROM visits;
```

---

## 4. OG 썸네일이 SNS에 안 뜸

### 증상

카카오톡/트위터/페이스북에 링크를 붙여넣으면 OG 썸네일이 비어 있음.

### 원인 1: og.jpg 파일 자체가 없음

`<meta property="og:image" content="https://domain.com/og.jpg">` 태그는 있는데
실제 파일이 서버에 없는 경우. SNS 크롤러가 404를 받아 이미지를 표시 안 함.

**해결**: Pillow로 og.jpg 생성 후 배포 디렉토리에 업로드.

```python
# make_og.py — 1200×630 OG 이미지 생성
from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGB', (1200, 630), '#0d1117')
draw = ImageDraw.Draw(img)
# ... 텍스트/도형 그리기 ...
img.save('/var/www/poli/og.jpg', 'JPEG', quality=90)
```

```bash
sudo apt install python3-pillow -y   # Pillow 설치
# 한글 폰트
sudo apt install fonts-noto-cjk -y
python3 make_og.py
```

### 원인 2: 캐시 (이전 404가 캐시됨)

SNS가 이전의 404 응답을 캐시해서 파일을 올려도 계속 안 보임.

**해결**: og:image URL에 버전 쿼리스트링 추가:

```html
<meta property="og:image" content="https://domain.com/og.jpg?v=1">
```

파일을 바꿀 때마다 `?v=2`, `?v=3` 으로 올려 캐시 무효화.

> 카카오 디버거: https://developers.kakao.com/tool/clear/og
> 페이스북 디버거: https://developers.facebook.com/tools/debug/
