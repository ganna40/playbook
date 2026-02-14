# [DEPLOY] EC2 배포 파이프라인

> 개발 완료 → EC2 서버 배포 → 서브도메인 연결 → 완료.

## 전체 흐름

```
1. 로컬에서 개발/테스트
2. SCP로 EC2에 업로드
3. Nginx 서브도메인 설정
4. SSL 인증서 (Cloudflare)
5. GitHub 백업
```

## 1. SCP 업로드

```bash
# 로컬 → 서버
scp -i "YOUR_PEM_KEY_PATH" -r \
  ./project/* YOUR_SSH_USER@YOUR_SERVER_IP:/var/www/프로젝트명/
```

## 2. Nginx 서브도메인 설정

```bash
# SSH 접속
ssh -i "YOUR_PEM_KEY_PATH" YOUR_SSH_USER@YOUR_SERVER_IP

# Nginx 설정 추가
sudo nano /etc/nginx/sites-available/프로젝트명
```

```nginx
server {
    listen 80;
    server_name 프로젝트명.pearsoninsight.com;
    root /var/www/프로젝트명;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

```bash
# 심볼릭 링크 + 재시작
sudo ln -s /etc/nginx/sites-available/프로젝트명 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 3. Cloudflare DNS 설정

1. Cloudflare 대시보드 → DNS
2. A 레코드 추가:
   - Name: `프로젝트명` (예: salary)
   - Content: `YOUR_SERVER_IP`
   - Proxy: ON (주황색 구름)
3. SSL: Full (strict)

## 4. GitHub 백업

```bash
# git-uploader 대시보드 사용
python app.py
# → EC2 서버 탭 → /var/www/프로젝트명 → 레포이름 → Upload
```

## 5. 완성 후 체크리스트

- [ ] 모바일에서 접속 테스트
- [ ] 카카오톡 공유 테스트
- [ ] OG 이미지 미리보기 확인 (https://developers.kakao.com/tool/debugger/sharing)
- [ ] Google Analytics 실시간 확인
- [ ] GitHub 백업 완료

## 자동화 (한번에)

```bash
# 로컬에서 개발 → 서버 업로드 → GitHub 백업 한번에
scp -i key.pem -r ./project/* ubuntu@3.34.190.131:/var/www/프로젝트명/ && \
cd /path/to/git-uploader && bash upload.sh /var/www/프로젝트명 프로젝트명
```

## 서버 정보

> 실제 값은 로컬 `_secrets.md` 참조.

| 항목 | 값 |
|------|-----|
| IP | `[비공개]` |
| OS | Ubuntu |
| User | `[비공개]` |
| Key | `[비공개]` |
| Web Root | /var/www/ |
| Nginx | /etc/nginx/sites-available/ |
| Domain | *.pearsoninsight.com |
