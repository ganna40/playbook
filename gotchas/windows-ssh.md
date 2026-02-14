# Windows + SSH 삽질 방지

## 1. SSH 유저명 확인

EC2 AMI마다 기본 유저가 다름:

| AMI | 유저명 |
|-----|--------|
| Ubuntu | `ubuntu` |
| Amazon Linux | `ec2-user` |
| CentOS | `centos` |
| Debian | `admin` |

PEM 키 이름 ≠ SSH 유저명. 헷갈리지 말 것.

## 2. PEM 키 권한

Windows OpenSSH가 키 파일 권한이 너무 넓으면 거부할 수 있음.
보통은 그냥 되지만, 안 되면:

```powershell
icacls "C:\Users\ganna\Downloads\key.pem" /inheritance:r
icacls "C:\Users\ganna\Downloads\key.pem" /grant:r "%USERNAME%:R"
```

## 3. Git Bash에서 경로 변환

Windows 경로 → Git Bash 유닉스 경로:

```bash
# Windows
C:\Users\ganna\Downloads\key.pem

# Git Bash
/c/Users/ganna/Downloads/key.pem
```

스크립트에서 자동 변환:
```bash
SSH_KEY_UNIX=$(echo "$SSH_KEY" | sed 's|\\|/|g' | sed 's|^\([A-Za-z]\):|/\1|')
```

## 4. SCP 첫 접속 멈춤

`StrictHostKeyChecking=no` 안 넣으면 호스트 키 확인 프롬프트에서 멈춤:

```bash
scp -o StrictHostKeyChecking=no -i key.pem ...
```

## 5. Cloudflare 뒤 서버

도메인이 Cloudflare에 있으면 `nslookup domain.com`으로 나오는 IP는 CDN IP임.
SSH는 실제 서버 퍼블릭 IP로 접속해야 함 (AWS 콘솔에서 확인).
