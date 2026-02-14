# 서버 → GitHub 파이프라인

> EC2 서버의 파일을 GitHub repo로 자동 업로드/업데이트.
> repo가 없으면 자동 생성 (private).

## 기술스택

| 항목 | 선택 |
|------|------|
| 전송 | SCP (SSH 기반) |
| 버전관리 | Git CLI |
| Repo 생성 | GitHub REST API |
| 인증 | Git Credential Manager (토큰 자동 추출) |

## 전체 흐름

```
서버 (SCP) → 로컬 임시폴더 → git clone 기존 repo
→ 파일 교체 → diff commit → push
```

## 핵심 코드

### 1. Git Credential Manager에서 토큰 추출

```python
import subprocess

def get_github_token():
    result = subprocess.run(
        [r"C:\Program Files\Git\mingw64\bin\git-credential-manager.exe", "get"],
        input="protocol=https\nhost=github.com\n",
        capture_output=True, text=True, timeout=10
    )
    for line in result.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1]
    return None
```

### 2. GitHub repo 자동 생성 (private)

```python
import urllib.request, json

def ensure_repo(github_user, repo_name, token):
    url = f"https://api.github.com/repos/{github_user}/{repo_name}"
    req = urllib.request.Request(url, headers={"Authorization": f"token {token}"})
    try:
        urllib.request.urlopen(req)
        return True, "이미 존재"
    except urllib.error.HTTPError as e:
        if e.code != 404:
            return False, f"API 오류: {e.code}"

    # 생성
    data = json.dumps({"name": repo_name, "private": True}).encode()
    req = urllib.request.Request(
        "https://api.github.com/user/repos", data=data, method="POST",
        headers={"Authorization": f"token {token}", "Content-Type": "application/json"}
    )
    urllib.request.urlopen(req)
    return True, "새로 생성됨"
```

### 3. 히스토리 보존 업데이트 (clone → 교체 → commit)

```python
import shutil

# 1. 기존 repo clone
run_cmd(f'git clone --depth=1 {repo_url} "{work_dir}"')

# 2. 기존 파일 삭제 (.git 제외)
for item in work_dir.iterdir():
    if item.name == ".git":
        continue
    if item.is_dir():
        shutil.rmtree(item)
    else:
        item.unlink()

# 3. 새 파일 복사
shutil.copytree(source_dir, work_dir, dirs_exist_ok=True)

# 4. 변경분만 커밋
run_cmd('git add -A', cwd=work_dir)
run_cmd('git commit -m "Update"', cwd=work_dir)
run_cmd('git push', cwd=work_dir)
```

### 4. SCP로 서버 파일 다운로드

```bash
scp -i "key.pem" -o StrictHostKeyChecking=no -r \
    ubuntu@1.2.3.4:/var/www/project/* /local/path/
```

## 주의사항

- `--depth=1` 으로 clone해야 속도 빠름 (전체 히스토리 불필요)
- `.git` 폴더는 절대 삭제하면 안 됨 (히스토리 유지)
- force push는 최후 수단 (히스토리 날아감)
- SCP에 `StrictHostKeyChecking=no` 안 하면 첫 접속 시 멈춤

## AI 프롬프트 예시

```
서버에서 파일을 가져와서 GitHub에 올리는 스크립트를 만들어줘.
- SCP로 다운로드
- repo 없으면 private으로 자동 생성
- 기존 repo는 히스토리 유지하면서 업데이트
- 위 레시피를 참고해서 구현해줘
```
