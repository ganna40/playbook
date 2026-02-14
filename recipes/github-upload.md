# GitHub 업로드 가이드

> 프로젝트를 GitHub에 올리는 방법. CLI와 웹 두 가지.

## 방법 1: Git CLI (권장)

### 새 프로젝트 처음 올리기

```bash
# 1. 프로젝트 폴더로 이동
cd C:\Users\ganna\Downloads\my-project

# 2. Git 초기화
git init

# 3. 파일 추가 + 커밋
git add -A
git commit -m "initial commit"

# 4. GitHub에 repo 생성 (gh CLI 사용)
gh repo create my-project --private --source=. --push

# 또는 수동으로:
git remote add origin https://github.com/ganna40/my-project.git
git branch -M main
git push -u origin main
```

### 기존 프로젝트 업데이트

```bash
cd C:\Users\ganna\Downloads\my-project
git add -A
git commit -m "설명"
git push origin main
```

### 서버에서 파일 가져와서 GitHub에 올리기

```bash
# 1. SCP로 서버 파일 다운로드
scp -i "key.pem" -o StrictHostKeyChecking=no -r \
    ubuntu@서버IP:/var/www/html/project/* C:\Users\ganna\Downloads\temp-project\

# 2. GitHub에 올리기
cd C:\Users\ganna\Downloads\temp-project
git init && git add -A && git commit -m "initial commit"
gh repo create project-name --private --source=. --push
```

> 자세한 서버→GitHub 파이프라인은 [server-to-github 레시피](recipes/server-to-github.md) 참조.

## 방법 2: GitHub 웹 (GUI)

### 새 repo 만들기

1. https://github.com/new 접속
2. **Repository name** 입력 (예: `my-project`)
3. **Private** 또는 **Public** 선택
4. **Create repository** 클릭

### 파일 업로드

1. 생성된 repo 페이지에서 **"uploading an existing file"** 클릭
2. 파일/폴더를 **드래그 앤 드롭** (또는 "choose your files" 클릭)
3. Commit message 입력
4. **Commit changes** 클릭

> 제한: 파일 하나당 25MB, 한 번에 100개까지만 업로드 가능.

### 기존 repo에 파일 추가/수정

1. repo 페이지에서 **Add file → Upload files** 클릭
2. 파일 드래그 앤 드롭
3. Commit changes 클릭

### 웹에서 직접 파일 편집

1. 수정할 파일 클릭
2. 연필 아이콘 (✏️ Edit) 클릭
3. 수정 후 **Commit changes** 클릭

## 방법 3: GitHub Desktop (GUI 앱)

```
1. https://desktop.github.com/ 에서 설치
2. GitHub 계정 로그인
3. File → Add Local Repository (기존 프로젝트)
   또는 File → Clone Repository (GitHub에서 가져오기)
4. 변경사항이 자동으로 감지됨
5. Summary 입력 → Commit to main → Push origin
```

## gh CLI 설치 (GitHub CLI)

```bash
# Windows (winget)
winget install GitHub.cli

# 로그인
gh auth login
```

## .gitignore 필수 항목

```bash
# 민감 정보
.env
_secrets.md
*.pem
credentials.json

# OS 파일
.DS_Store
Thumbs.db

# 의존성
node_modules/
__pycache__/
venv/

# 빌드 결과물
dist/
build/
```

## Git 설정 확인

```bash
# 현재 설정 확인
git config --global user.name
git config --global user.email

# 설정 변경
git config --global user.name "ganna40"
git config --global user.email "eyeom40@gmail.com"
```

## 자주 쓰는 명령어

| 명령어 | 설명 |
|--------|------|
| `git status` | 변경된 파일 목록 |
| `git add -A` | 모든 변경 스테이징 |
| `git commit -m "msg"` | 커밋 |
| `git push origin main` | 푸시 |
| `git pull origin main` | 풀 (서버→로컬) |
| `git log --oneline -5` | 최근 5개 커밋 로그 |
| `git diff` | 변경 내용 확인 |
| `git clone URL` | repo 복제 |
| `gh repo create NAME --private` | 새 repo 생성 |

## 주의사항

- **민감 정보** (API 키, 비밀번호, PEM 키)는 **절대** GitHub에 올리지 말 것
- `.gitignore`에 등록하기 **전에** 커밋한 파일은 이미 히스토리에 남음 → `git rm --cached 파일명`으로 제거
- public repo는 **누구나** 볼 수 있음. 민감한 프로젝트는 반드시 **private**
- 대용량 파일 (100MB+)은 [Git LFS](https://git-lfs.github.com/) 사용
