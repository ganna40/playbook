# naver-monitor - 네이버 카페 키워드 모니터링 + 정산

> GitHub: https://github.com/ganna40/navercafe_monitoring
> 로컬: C:\Users\ganna\Downloads\cafe-monitor
> 스택: FastAPI + SQLAlchemy + MariaDB + Playwright + TypeScript SPA

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 풀스택 모니터링 + 정산 시스템 |
| **한줄 설명** | 네이버 카페 키워드 노출 확인 + 댓글 감지 + 결재/정산 자동화 |
| **타겟** | 바이럴 마케팅 담당자 (캠페인별 검증 + 정산 관리) |
| **테마** | 라이트 (Tailwind v4) |

## 기술 스택

```
백엔드: FastAPI + SQLAlchemy(sync) + PyMySQL + MariaDB
크롤링: Playwright (headless Chromium) + API 인터셉트
프론트: TypeScript + Vite + Tailwind CSS v4 (Vanilla SPA)
```

## 핵심 아키텍처

```
[캠페인 등록] → 이름 + 건당 단가
    ↓
[검증 건 등록] → 작성자/제목/검색키워드/감지키워드
    ↓
[검증 실행] Playwright로 네이버 검색 → 제목 매칭 → 댓글 API 인터셉트
    ↓
감지됨 / 미감지 / 미노출
    ↓ (자동 재검증 ON이면)
[재검증 루프] → 2회 연속 감지 시 자동 결재 요청
    ↓
[결재] 관리자 승인/반려
    ↓
[정산] 캠페인 단가 기준 자동 계산
```

## 주요 기능

| 기능 | 설명 |
|------|------|
| **API 인터셉트 댓글 감지** | DOM 스크래핑 대신 `page.on("response")` 로 댓글 API 응답 캡처 (비로그인 제한 우회) |
| **Best-match 제목 매칭** | 점수 기반 매칭 (70% 길이 비율 threshold) — 부분 일치 오탐 방지 |
| **자동 재검증** | 미감지 시 N초 간격으로 최대 M회 재시도, 에러 시에도 계속 진행 |
| **2회 연속 감지 → 자동 결재** | 신뢰성 확보 후 자동 결재 요청 |
| **개별 페이지 권한** | admin/user 외에 결재/정산/로그 페이지를 개별 부여 가능 |
| **검증 이력** | 차수별(1차, 2차...) 결과/순위/댓글수/소요시간 기록 |
| **실시간 타이머** | 검증 실행 중 경과 시간 표시 |
| **세션 유지** | sessionStorage로 로그인 + 현재 탭 유지 |
| **서버 설정 영속** | DB 기반 key-value 설정 (로그아웃해도 유지) |
| **페이지네이션** | 캠페인/검증 목록 10/20/50개씩 표시 |

## 핵심 레시피: 댓글 API 인터셉트

```python
# _crawl_worker.py — DOM 스크래핑 대신 API 응답 캡처
captured = []

def on_response(resp):
    url = resp.url
    if "/CommentView.nhn" in url or "/comment/list" in url:
        try:
            body = resp.json()
            # result.commentList[].contents 에서 댓글 텍스트 추출
            comments = body.get("result", {}).get("commentList", [])
            for c in comments:
                captured.append(c.get("contents", ""))
        except: pass

page.on("response", on_response)
page.goto(url)  # 댓글 API 자동 호출됨 → captured에 수집
```

## 핵심 레시피: 제목 매칭 (오탐 방지)

```python
def match_title_score(search_title, result_title):
    s = re.sub(r'[^\w]', '', search_title.lower())
    r = re.sub(r'[^\w]', '', result_title.lower())
    if s == r: return 1.0
    shorter, longer = (s, r) if len(s) <= len(r) else (r, s)
    if shorter in longer:
        ratio = len(shorter) / len(longer)
        if ratio >= 0.7: return ratio  # 70% 이상이면 허용
    return 0.0

# 가장 높은 점수의 게시글 선택
matched = max(search_results, key=lambda x: match_title_score(title, x["title"]))
```

## DB 모델

```
User        — username, password, role, permissions(JSON), approved
Campaign    — name, price_per_post
Verification — campaign_id, writer_name, post_title, search/detect_keyword,
               status, rank, total_comments, detected_positions, post_url
VerificationLog — verification_id, attempt, status, rank, elapsed_seconds
Approval    — verification_id, requested_by, approved_by, status, note
AppSetting  — key, value (서버 설정 영속)
ActivityLog — username, method, path, status_code, detail
```

## 파일 구조

```
cafe-monitor/
├── main.py              # FastAPI 앱 (REST API + 미들웨어)
├── models.py            # SQLAlchemy 모델
├── schemas.py           # Pydantic 스키마
├── database.py          # DB 연결 설정
├── _crawl_worker.py     # Playwright 크롤링 워커 (subprocess)
├── requirements.txt     # fastapi, uvicorn, sqlalchemy, pymysql, playwright
└── frontend/
    ├── vite.config.ts   # Vite + Tailwind v4 + 프록시(/api → :8000)
    └── src/
        ├── main.ts      # SPA 라우팅 + 상태 + 권한 체크
        ├── api.ts       # fetch 래퍼
        └── pages/
            ├── dashboard.ts      # 통합 요약 + 최근 항목
            ├── campaigns.ts      # 캠페인 CRUD + 페이지네이션
            ├── verifications.ts  # 검증 관리 + 재검증 루프 + 타이머
            ├── approvals.ts      # 결재 승인/반려
            ├── settlement.ts     # 정산 처리
            ├── settings.ts       # 사용자 권한 + 자동 재검증 설정
            ├── logs.ts           # 활동 로그
            └── login.ts          # 로그인/회원가입
```

## Docker 배포 (원클릭 설치)

> 로컬: C:\Users\ganna\Downloads\cafe-monitor-docker

Docker Compose로 MariaDB + FastAPI + Vite 프론트엔드를 한 번에 띄우는 버전.
Python, Node.js, MariaDB 설치 없이 Docker만 있으면 실행 가능.

### 실행

```bash
# Windows — 더블클릭
start.bat

# Mac / Linux
chmod +x start.sh && ./start.sh
```

Docker가 없으면 자동 설치 시도. 첫 실행 시 5~10분 (이미지 빌드), 이후 10초.

### 구성

```yaml
# docker-compose.yml
services:
  db:        # MariaDB 11 — 포트 3306
  backend:   # FastAPI + Playwright — 포트 8000
  frontend:  # Vite dev server — 포트 3000 (프록시 → backend)
```

| 컨테이너 | 이미지 | 핵심 |
|----------|--------|------|
| db | mariadb:11 | root/cafe1234, DB: cafe_monitor |
| backend | python:3.12-slim + Playwright chromium | wait-for-db.py로 DB 대기 후 uvicorn 실행 |
| frontend | node:20 | API_URL=http://backend:8000, Vite 프록시 |

### 폐쇄망 배포

인터넷 PC에서 이미지를 빌드 → 파일로 저장 → USB로 이동:

```bash
# 인터넷 PC
docker compose build
docker save cafe-monitor-docker-backend cafe-monitor-docker-frontend mariadb:11 \
  | gzip > cafe-monitor-images.tar.gz

# 폐쇄망 PC (Docker만 설치되어 있으면 됨)
docker load < cafe-monitor-images.tar.gz
docker compose up -d    # --build 없이!
```

USB에 담을 것: Docker 설치파일(~500MB) + 이미지(~2-3GB) + docker-compose.yml

### 파일 구조

```
cafe-monitor-docker/
├── docker-compose.yml    # 3개 서비스 정의
├── Dockerfile            # backend (Python 3.12 + Playwright)
├── wait-for-db.py        # DB 연결 대기 (30회 폴링)
├── start.bat             # Windows 원클릭 (Docker 설치+실행+compose up)
├── start.sh              # Mac/Linux 원클릭
├── database.py           # MariaDB 전용 (SQLite 없음)
├── main.py / models.py / schemas.py / _crawl_worker.py
├── requirements.txt
└── frontend/
    ├── Dockerfile        # Node 20 + npm install + vite
    └── vite.config.ts    # API_URL 환경변수로 backend 연결
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 naver-monitor 레퍼런스를 보고
"네이버 블로그 키워드 순위 모니터링 + 정산 시스템"을 만들어줘.

- FastAPI + SQLAlchemy + MariaDB
- Playwright API 인터셉트로 댓글/반응 감지
- TypeScript + Vite + Tailwind v4 SPA
- 캠페인 > 검증 > 결재 > 정산 워크플로우
- 자동 재검증 + 개별 페이지 권한
```
