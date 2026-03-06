# naver-monitor - 네이버 카페 키워드 순위 모니터링

> 로컬: C:\Users\ganna\Downloads\naver-monitor
> 스택: FastAPI + SQLAlchemy async + MariaDB + Playwright + APScheduler

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 백엔드 모니터링 도구 (키워드 순위 추적 + 댓글 검증) |
| **한줄 설명** | 네이버 통합검색에서 카페 글 노출/댓글 브랜드명 검증 자동화 |
| **타겟** | 바이럴 마케팅 담당자 (키워드별 노출 추적 + 정산 관리) |
| **테마** | 다크 (GitHub 스타일) |
| **폰트** | 시스템 폰트 |

## 기술 스택

```
FastAPI + SQLAlchemy(async/aiomysql) + MariaDB
Playwright (headless Chromium) + BeautifulSoup(lxml)
APScheduler (AsyncIOScheduler)
Naver Search API (cafearticle)
Slack Webhook + Google Sheets API (gspread)
Vanilla JS SPA (단일 index.html)
```

## 핵심 아키텍처

```
[등록] 키워드+브랜드 → DB (대기)
    ↓
[수동] 담당자가 순위/URL 입력 → DB (노출확인)
    ↓ 24H 후 자동
[검증] 통합검색 → 카페 글 전체 → 댓글에서 brand_name 검사
    ↓
건바이 성공 / 미노출AS / 판단불가
    ↓
[수동] 정산 이관 → 정산대기 → 입금완료
```

## 특수 기능 (핵심 레시피)

| 기능 | 설명 |
|------|------|
| **네이버 카페 댓글 크롤링** | `?art=` JWT 토큰으로 로그인 없이 카페 글 접근 → iframe 내 Vue SPA 렌더링 대기 → 실제 댓글 추출 |
| **Playwright Stealth** | webdriver 속성 숨기기 + AutomationControlled 비활성화 |
| **통합검색 진입** | `search.naver.com?query=keyword` (탭 이동 없이 카페 영역 식별) |
| **subprocess 분리** | Windows uvicorn 이벤트 루프에서 Playwright 실행 불가 → 별도 Python 프로세스 |
| **랜덤 딜레이** | 게시글 순차 접속 시 2~5초 랜덤 대기 (탐지 회피) |

## 네이버 카페 댓글 인식 흐름 (★ 핵심 레시피)

```
1. 통합검색에서 cafe.naver.com 링크 중 ?art= 토큰 포함 URL 추출
   → ?art= 는 검색 결과에서만 발급되는 JWT 토큰 (로그인 불필요 접근 허용)

2. ?art= URL로 카페 글 접속
   → 페이지 구조: 메인 페이지 > #cafe_main iframe > Vue SPA (#app)

3. Vue SPA 렌더링 대기
   → iframe.evaluate("document.getElementById('app').innerHTML.length")
   → 1000자 이상이면 렌더링 완료 (미렌더링 시 49자: "JavaScript enabled" 에러 메시지)
   → 최대 10회 × 1.5초 폴링

4. 스크롤 후 댓글 추출
   → iframe.evaluate("window.scrollTo(0, document.body.scrollHeight)")
   → 셀렉터: .comment_text_box .text_comment
   → 실제 사용자 댓글만 추출 (제목/본문 아님)

5. 브랜드명 매칭
   → 댓글 텍스트에서 brand_name (키워드 아님!) 포함 여부 검사
   → 1개라도 매칭되면 건바이 성공
```

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| **Playwright** | headless Chromium으로 네이버 검색/카페 크롤링 |
| **?art= JWT 토큰** | 검색 결과 URL에 포함된 카페 접근 토큰 (로그인 불필요) |
| **cafe_main iframe** | 네이버 카페 글은 iframe 안에 Vue SPA로 렌더링 |
| **subprocess.run + asyncio.to_thread** | uvicorn 이벤트 루프에서 Playwright 분리 실행 |
| **Naver Search API** | cafearticle 검색 (일 25,000건, Playwright fallback) |
| **APScheduler** | 24H 후 자동 검증 스케줄러 |
| **Slack Webhook** | 상태 변경 알림 (노출확인, 미노출 등) |
| **gspread** | Google Sheets 실시간 연동 |

## 파일 구조

```
naver-monitor/
├── main.py                          # FastAPI 앱 (lifespan, 미들웨어)
├── .env                             # API 키, DB URL 등
├── static/
│   ├── index.html                   # 다크 대시보드 (Vanilla JS SPA)
│   └── login.html                   # 로그인 페이지
├── app/
│   ├── core/
│   │   ├── config.py                # Pydantic Settings
│   │   └── database.py              # SQLAlchemy async 설정
│   ├── models/
│   │   └── models.py                # Keyword, StatusLog, Settlement, User
│   ├── api/
│   │   └── routes.py                # REST API (CRUD + 수동확인 + 검증 + 정산)
│   └── services/
│       ├── naver_search.py          # Naver API + Playwright 검색
│       ├── _comment_worker.py       # ★ 댓글 검증 워커 (subprocess로 실행)
│       ├── comment_checker.py       # subprocess 래퍼 (asyncio.to_thread)
│       ├── scheduler.py             # 24H 자동 검증 스케줄러
│       ├── slack_service.py         # Slack Webhook 알림
│       └── sheets_service.py        # Google Sheets 연동
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 naver-monitor 레퍼런스를 보고
"네이버 블로그 키워드 모니터링 도구"를 만들어줘.

- FastAPI + SQLAlchemy async + MariaDB
- Playwright로 네이버 검색 크롤링
- 키워드별 순위 추적 + 자동 재점검
- naver-monitor의 댓글 크롤링 기법 (_comment_worker.py 참고)
- 다크 대시보드 UI
```
