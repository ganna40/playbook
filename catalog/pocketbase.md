# [POCKETBASE] BaaS (DB + 인증 + 파일 + API)

> 백엔드를 빠르게 구축할 때 사용. DB + 인증 + 파일 저장 + REST API를 한번에.
> 의존: 없음

## PocketBase란

- Go로 만든 **1개 바이너리 BaaS** (Backend as a Service)
- SQLite 기반 DB + 인증 + 파일 저장 + REST API + Admin UI
- 실행만 하면 `http://127.0.0.1:8090/_/`에서 테이블/인증/파일 관리
- Firebase의 셀프호스팅 대안

## 설치 및 실행

```bash
# 다운로드 (https://pocketbase.io/docs/)
# Windows: pocketbase.exe, Linux: pocketbase 바이너리

# 실행
./pocketbase serve
# → http://127.0.0.1:8090 (API)
# → http://127.0.0.1:8090/_/ (Admin UI)
```

## 필요 라이브러리 (Python)

```bash
pip install pocketbase requests
```

## 핵심 코드

### 초기화 + 인증

```python
from pocketbase import PocketBase

pb = PocketBase('http://127.0.0.1:8090')

# 로그인
auth_data = pb.collection('users').auth_with_password(email, password)
token = auth_data.token
user = auth_data.record
```

### CRUD 기본

```python
# 생성 (Create)
record = pb.collection('tasks').create({
    "title": "새 태스크",
    "priority": "urgent",
    "status": "todo",
    "assignee": "USER_ID",  # relation 필드
})

# 읽기 (Read) - 전체 목록
tasks = pb.collection('tasks').get_full_list(
    query_params={
        'filter': 'status != "completed"',
        'sort': '-created',
        'expand': 'assignee',  # 관계 데이터 포함
    }
)

# 읽기 - 단건
task = pb.collection('tasks').get_one(task_id)

# 수정 (Update)
pb.collection('tasks').update(task_id, {
    "status": "completed"
})

# 삭제 (Delete)
pb.collection('tasks').delete(task_id)
```

### 필터 쿼리

```python
# 텍스트 검색
filter_query = 'title ~ "검색어" || content ~ "검색어"'

# 상태 필터
filter_query = 'status = "ongoing" && priority = "urgent"'

# 날짜 필터
filter_query = 'due_date <= "2026-02-14"'

# 관계 필터
filter_query = 'assignee = "USER_ID"'

tasks = pb.collection('tasks').get_full_list(
    query_params={'filter': filter_query}
)
```

### 관계(Relation) 데이터 확장

```python
# expand로 관계 데이터 가져오기
tasks = pb.collection('tasks').get_full_list(
    query_params={'expand': 'assignee'}
)

# 사용
for task in tasks:
    expand = getattr(task, 'expand', {})
    if expand and 'assignee' in expand:
        assignees = expand['assignee']
        names = [u.name for u in assignees]
```

### 파일 업로드

```python
import requests

api_url = f"http://127.0.0.1:8090/api/collections/tasks/records"
headers = {"Authorization": token}

# 단일 파일
with open("file.pdf", "rb") as f:
    files = {'attachment': ('file.pdf', f.read())}
    resp = requests.post(api_url, headers=headers, data=payload, files=files)

# 다중 파일
files_to_send = []
for f in uploaded_files:
    files_to_send.append(('attachment', (f.filename, f.read())))
resp = requests.post(api_url, headers=headers, data=payload, files=files_to_send)
```

### 파일 다운로드

```python
# PocketBase 파일 URL 패턴
file_url = f"http://127.0.0.1:8090/api/files/{collection_id}/{record_id}/{filename}"
```

## Flask 통합 패턴 (collab-tool 참조)

```python
# config.py
class Config:
    POCKETBASE_URL = 'http://127.0.0.1:8090'
    PERMANENT_SESSION_LIFETIME = 3600

# services/pb_service.py
from pocketbase import PocketBase
from config import Config
pb = PocketBase(Config.POCKETBASE_URL)

# app.py (인증 체크)
@app.before_request
def check_auth():
    if request.endpoint not in ('login', 'register', 'static'):
        if 'token' not in session:
            return redirect(url_for('login'))
        pb.auth_store.save(session['token'], None)
```

## Admin UI 활용

```
http://127.0.0.1:8090/_/

기능:
- 컬렉션(테이블) 생성/관리
- 필드 타입: text, number, bool, date, file, relation, json, select
- 인증 설정 (이메일/비번, OAuth)
- API 규칙 (CRUD 권한 설정)
- 파일 저장소 관리
- 실시간 로그
```

## 주의사항

- **SQLite 기반**: 동시 쓰기가 많으면 병목. 소규모 팀 도구에 적합
- **바이너리 1개**: 설치 없이 실행 파일만으로 동작. 배포 간단
- **마이그레이션**: Admin UI에서 스키마 변경 → `pb_migrations/` 폴더에 자동 기록
- **백업**: `pb_data/` 폴더만 백업하면 전체 데이터 보존
- **파일 크기**: 기본 5MB 제한, Admin에서 변경 가능
- **Python SDK 제한**: 공식 SDK는 JS/Dart. Python은 커뮤니티 패키지 (`pocketbase` pip)
- **토큰 만료**: PocketBase 토큰은 기본 2주 유효. Flask 세션으로 별도 관리 권장

## 사용 예시

```python
# collab-tool 패턴: Flask + PocketBase
# 1. PocketBase 실행 (./pocketbase serve)
# 2. Admin에서 컬렉션 생성 (tasks, kpis, warehouse 등)
# 3. Flask에서 pb.collection('tasks').get_full_list() 호출
# 4. Jinja2 템플릿에서 데이터 렌더링
```
