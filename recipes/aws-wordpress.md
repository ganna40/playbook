# AWS WordPress - EC2에 워드프레스 설치

> Ubuntu EC2에 LAMP 스택(Apache + MySQL + PHP) + WordPress.
> 무료 티어 기준 t3.micro/small 1대 운영.
> 원문: https://pearsoninsight.com/aws-워드프레스-설치/

## 무료 티어 한도

| 항목 | 한도 | 비고 |
|------|------|------|
| EC2 인스턴스 | t3.micro/small **월 750시간** | 24h × 31일 = 744시간 → 1대 상시 가능 |
| EBS 스토리지 | **30GB** (gp3 SSD) | 기본 8GB → 30GB로 설정 |
| 데이터 전송 | 월 **100GB** 아웃바운드 | 블로그 초기에는 충분 |
| 기간 | 계정 생성일로부터 **12개월** | 2025.07.15 이후 가입 = 6개월 |

⚠️ 인스턴스 **2개 이상** 띄우면 시간 합산 → 750시간 초과 과금. **1대만** 운영.

## EC2 인스턴스 생성

EC2 대시보드 → "인스턴스 시작". 리전을 **서울(ap-northeast-2)**로 확인.

| 항목 | 설정값 | 이유 |
|------|--------|------|
| 이름 | `my-wordpress-blog` | 원하는 이름 |
| OS (AMI) | **Ubuntu** | 자료 많아서 트러블슈팅 편함 |
| 인스턴스 유형 | **t3.micro** 또는 **t3.small** | "무료 티어 사용 가능" 라벨 확인 |
| 키 페어 | 새로 생성 → **.pem** 다운로드 | 분실하면 서버 접속 불가 |
| 퍼블릭 IP | **자동 할당 활성화** | 안 켜면 외부 접속 불가 |
| 스토리지 | **30GB gp3** | 무료 한도 최대치, 나중에 부족 방지 |
| Credit spec | **Standard** | Unlimited는 CPU 과다 시 추가 과금 |

### 보안 그룹

| 유형 | 포트 | 소스 | 용도 |
|------|------|------|------|
| SSH | 22 | **내 IP** | 서버 접속 (0.0.0.0/0 절대 금지) |
| HTTP | 80 | 0.0.0.0/0 | 웹사이트 |
| HTTPS | 443 | 0.0.0.0/0 | SSL 웹사이트 |

> SSH 소스를 `0.0.0.0/0`으로 두면 보안 경고. IP 바뀌면 보안 그룹에서 수정하면 됨.
> 보안 강화는 [EC2 보안 삽질 방지](gotchas/ec2-security.md) 참조.

## SSH 접속

인스턴스 "실행 중" 확인 → 퍼블릭 IPv4 주소 복사.

```bash
# Windows (PowerShell)
ssh -i "C:\Users\사용자이름\Downloads\키파일.pem" ubuntu@퍼블릭IP

# Mac/Linux
chmod 400 ~/Downloads/키파일.pem
ssh -i ~/Downloads/키파일.pem ubuntu@퍼블릭IP
```

`ubuntu@ip-xxx-xxx:~$` 프롬프트가 보이면 접속 성공.

> Windows SSH 문제는 [Windows + SSH 삽질 방지](gotchas/windows-ssh.md) 참조.

## LAMP 스택 설치

```bash
# 패키지 업데이트
sudo apt update && sudo apt upgrade -y

# Apache + MySQL + PHP 한 번에
sudo apt install apache2 mysql-server php php-mysql php-curl php-gd php-xml php-mbstring -y
```

브라우저에서 `http://퍼블릭IP` → Apache 기본 페이지 뜨면 성공.

## MySQL 데이터베이스 설정

```bash
sudo mysql
```

```sql
CREATE DATABASE wordpress;
CREATE USER 'wpuser'@'localhost' IDENTIFIED BY '여기에강력한비밀번호';
GRANT ALL PRIVILEGES ON wordpress.* TO 'wpuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

> 비밀번호: 대문자+소문자+숫자+특수문자 조합. 다음 단계에서 다시 필요하니 메모.

## WordPress 다운로드

```bash
cd /tmp
curl -O https://wordpress.org/latest.tar.gz    # 최신 버전 다운로드
tar xzvf latest.tar.gz                          # 압축 해제
sudo cp -a /tmp/wordpress/. /var/www/html/      # 웹서버 폴더로 복사
sudo chown -R www-data:www-data /var/www/html/  # Apache 읽기/쓰기 권한
sudo rm /var/www/html/index.html                # Apache 기본 페이지 삭제
```

## Apache 설정 (퍼머링크)

> ⚠️ 이 단계를 빠뜨리면 고유주소 변경 시 404 에러. 실제로 겪은 문제.

```bash
sudo a2enmod rewrite
sudo nano /etc/apache2/apache2.conf
```

`<Directory /var/www/>` 블록에서 `AllowOverride None` → `AllowOverride All` 변경:

```apache
<Directory /var/www/>
    Options Indexes FollowSymLinks
    AllowOverride All
    Require all granted
</Directory>
```

```bash
sudo systemctl restart apache2
```

## 브라우저에서 설치 완료

`http://퍼블릭IP` → WordPress 설치 화면 → 언어 선택 후 DB 정보 입력:

| 항목 | 입력값 |
|------|--------|
| 데이터베이스 이름 | `wordpress` |
| 사용자명 | `wpuser` |
| 비밀번호 | MySQL에서 설정한 비밀번호 |
| 호스트 | `localhost` |
| 테이블 접두어 | `wp_` (기본값) |

"설치 실행" → 사이트 제목 + 관리자 계정 설정 → "워드프레스 설치" → 완료.

## 초기 설정

`http://퍼블릭IP/wp-admin` 접속.

### 고유주소

설정 → 고유주소 → **"글 이름"** 선택 → 저장.
URL이 `?p=123` → `/글-제목/` 형태 → SEO 유리.

### 추천 플러그인

| 플러그인 | 용도 | 비고 |
|----------|------|------|
| **Rank Math SEO** | 검색 노출 최적화 | 구글 검색 잘 되게 |
| **WP Super Cache** | 페이지 캐시 | t3.micro는 성능 낮으니 필수 |
| **Wordfence Security** | 보안 | 해킹 시도 차단 |

### 테마

기본(Twenty Twenty-Five)도 가능. 속도 중요하면 **GeneratePress** (무료) 추천.
모양 → 테마 → 새로 추가 → "GeneratePress" 검색 → 설치.

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| 브라우저 접속 안 됨 | 보안 그룹 HTTP(80) 미설정 | EC2 → 보안 그룹 → 인바운드에 HTTP 추가 |
| Apache 기본 페이지만 뜸 | index.html이 index.php보다 우선 | `dir.conf` 수정 (아래) |
| PHP 코드가 텍스트로 출력 | PHP 모듈 미활성화 | `a2enmod` 설정 (아래) |
| 고유주소 변경 후 404 | AllowOverride 미설정 | Apache 설정 단계 재확인 |
| 서버가 자주 죽음 | OOM Kill (메모리 부족) | [EC2 OOM Kill + Swap](gotchas/ec2-oom-swap.md) |

### Apache 기본 페이지만 뜰 때

```bash
sudo nano /etc/apache2/mods-enabled/dir.conf
```

```apache
# index.php를 맨 앞으로 이동
DirectoryIndex index.php index.html index.cgi index.pl index.xhtml index.htm
```

```bash
sudo systemctl restart apache2
```

### PHP 코드가 텍스트로 출력될 때

```bash
# php -v로 버전 확인 후 번호 맞추기
sudo a2enmod php8.3
sudo a2dismod mpm_event
sudo a2enmod mpm_prefork
sudo systemctl restart apache2
```

## 설치 후 로드맵

> 1~2번은 [WordPress 도메인+SSL 레시피](recipes/wordpress-domain-ssl.md) 참조.

| 순서 | 작업 | 비용 |
|------|------|------|
| 1 | 도메인 연결 + DNS 설정 (Cloudflare 추천) | 연 ~13,000원 |
| 2 | HTTPS 설정 (Cloudflare SSL 자동 적용) | 무료 |
| 3 | Google Search Console 등록 | 무료 |
| 4 | SEO 맞춤 글 10개+ 작성 | - |
| 5 | Google AdSense 신청 | 무료 |

## 비용 정리

| 항목 | 비용 | 비고 |
|------|------|------|
| EC2 인스턴스 | **무료** (12개월) | t3.micro/small |
| EBS 30GB | **무료** (12개월) | gp3 SSD |
| 데이터 전송 | **무료** (월 100GB) | 블로그 초기 충분 |
| 도메인 (선택) | 연 1~2만원 | 나중에 필요 시 구매 |
| **합계** | **0원~2만원/년** | 호스팅 월 4~5만원 대비 압도적 |

> 무료 기간 종료 후: Lightsail 이전 또는 EC2 유지 (월 ~1만원).

## 주의사항

- **키 페어 .pem 파일** 분실 = 서버 접속 불가. 안전한 곳에 보관
- SSH 소스를 **0.0.0.0/0으로 절대 열지 말 것**. "내 IP"만 허용
- Credit specification은 반드시 **Standard**. Unlimited = 추가 과금
- 인스턴스 **"종료" = 삭제**, **"중지" = 일시정지**. 헷갈리지 말 것
- 스토리지 8GB 기본값 두지 말고 처음부터 **30GB**로 설정

## AI 프롬프트 예시

```
AWS EC2(Ubuntu)에 WordPress를 설치해줘.
- t3.micro, 30GB gp3, 서울 리전
- LAMP 스택: Apache + MySQL + PHP
- WordPress 최신 버전 다운로드 + 권한 설정
- Apache mod_rewrite + AllowOverride All 설정
- MySQL DB: wordpress / wpuser 생성
- 위 레시피 명령어 순서대로 진행
```
