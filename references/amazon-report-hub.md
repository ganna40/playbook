# amazon-report-hub - Amazon 셀러 리포트 데이터 허브

> GitHub: https://github.com/ganna40/Amazon_report_hub

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 데이터 관리 도구 (리포트 허브) |
| **한줄 설명** | Amazon 5가지 리포트를 한 DB에 통합 — 업로드/동기화/조회/필터/삭제 |
| **타겟** | Amazon 셀러 운영팀 (Spigen US/CA FBA) |
| **테마** | 다크 (playbook style-dark 기반) |
| **폰트** | 시스템 폰트 (Segoe UI, Noto Sans KR) |

## 모듈 조합

```
Go(chi) + React19 + Vite + TailwindV4 + PostgreSQL(JSONB)
+ Embedded-PostgreSQL + go:embed + excelize(XLSX) + STYLE-DARK
```

## 핵심 아키텍처

```
[spigen-codex.exe — 단일 바이너리]
    ├── Embedded PostgreSQL (자동 시작/종료, 포트 5433)
    ├── HTTP REST API (chi 라우터, :8080)
    │     ├── /api/{reportType}/stats
    │     ├── /api/{reportType}/records (페이지네이션+필터)
    │     ├── /api/{reportType}/upload (multipart)
    │     ├── /api/{reportType}/sync-log
    │     └── /api/config
    ├── Frontend (React SPA, go:embed로 바이너리 내장)
    │     ├── Dashboard (통계 카드 + 채널 분포 차트)
    │     ├── Records (테이블 + 검색/필터/체크박스 삭제)
    │     ├── Upload (드래그앤드롭 + 진행률)
    │     ├── Batches (배치 이력)
    │     └── Config (JSON 에디터)
    └── IPC Mode (stdin/stdout JSON-line, Electron 호환)
         ↓
[PostgreSQL — JSONB]
    ├── rows (report_type + channel + data JSONB + GIN 인덱스)
    ├── batches (업로드/동기화 배치 메타데이터)
    ├── config (앱 설정 JSON)
    └── sync_log (동기화 이력)
```

## 기술 스택

| 구분 | 기술 | 설명 |
|------|------|------|
| **Backend** | Go 1.24 | 단일 바이너리, 크로스플랫폼 |
| | go-chi/chi v5 | 경량 HTTP 라우터 |
| | jackc/pgx v5 | PostgreSQL 드라이버 (배치 쿼리) |
| | xuri/excelize v2 | XLSX 파싱 |
| | fergusstrange/embedded-postgres | PostgreSQL 내장 실행 |
| | go:embed | 프론트엔드 바이너리 내장 |
| **Frontend** | React 19 + TypeScript | SPA 대시보드 |
| | Vite 6 | 빌드 도구 |
| | Tailwind CSS v4 | 유틸리티 CSS (다크 테마) |
| **Database** | PostgreSQL (JSONB) | 스키마리스 리포트 저장 |

## 주요 기능

| 기능 | 설명 |
|------|------|
| **스키마리스 저장** | 5가지 리포트 타입의 컬럼이 다 달라도 JSONB blob으로 통합 저장 |
| **채널 자동 감지** | sales-channel / ship-country 필드로 US FBA / CA FBA 자동 분류 |
| **파일 업로드** | CSV/TSV/XLSX 드래그앤드롭, append/replace 모드 |
| **Google Sheets 동기화** | sync 소스로 외부 데이터 연동 |
| **JSONB 검색** | PostgreSQL GIN 인덱스로 JSON 내부 필드 검색 |
| **배치 쿼리** | pgx.Batch로 1000건 청크 삽입 |
| **단일 바이너리 배포** | exe 하나에 PG + 프론트엔드 + API 전부 내장 |
| **IPC 호환** | --mode ipc로 Electron 앱과 stdin/stdout 통신 |
| **Mock 데이터** | --seed 플래그로 952건 리얼 데이터 자동 생성 |

## DB 스키마

```
rows: id(SERIAL), batch_id, report_type, channel, account, source, file_name, data(JSONB)
  인덱스: report_type, channel, source, batch_id, (rt,channel), (rt,source), data(GIN)

batches: id(TEXT PK), ts(TIMESTAMPTZ), report_type, source, account, file_name, total_rows, channel_counts(JSONB)

config: key(TEXT PK), value(JSONB)

sync_log: id(SERIAL), ts(TIMESTAMPTZ), status, message, detail(JSONB)
```

## 프로젝트 구조

```
spigen-codex/
├── main.go                    # 진입점 (embedded PG + 브라우저 자동 오픈)
├── go.mod
├── internal/
│   ├── store/
│   │   ├── store.go           # DB 연결 + 자동 생성 + 마이그레이션
│   │   └── queries.go         # 모든 쿼리 + 타입 정의
│   ├── parser/
│   │   └── parser.go          # CSV/TSV/XLSX + 채널 감지
│   ├── api/
│   │   └── api.go             # REST API + SPA 서빙
│   ├── ipc/
│   │   └── ipc.go             # stdin/stdout JSON-line
│   └── seed/
│       └── seed.go            # Mock 데이터 생성기
└── frontend/
    ├── src/                   # React 19 + TypeScript
    │   ├── App.tsx            # 사이드바 + 탭 라우팅
    │   ├── StatsView.tsx      # 대시보드
    │   ├── RecordsView.tsx    # 데이터 테이블
    │   ├── UploadView.tsx     # 파일 업로드
    │   └── ...
    └── dist/                  # go:embed로 바이너리에 내장
```

## 특수 패턴

| 패턴 | 설명 |
|------|------|
| **Embedded PostgreSQL** | `fergusstrange/embedded-postgres`로 PG를 서브프로세스로 실행. 첫 실행 시 바이너리 다운로드 후 캐시. |
| **go:embed SPA** | `//go:embed frontend/dist/*`로 빌드된 React를 바이너리에 내장. `fs.Sub`로 prefix 제거 후 `http.FileServerFS`로 서빙 + SPA fallback. |
| **JSONB 스키마리스** | 리포트마다 컬럼이 달라도 `data JSONB`에 통합. `data::text ILIKE`로 전문 검색, GIN 인덱스로 JSON 경로 쿼리. |
| **듀얼 모드 (HTTP/IPC)** | 같은 Store 레이어를 HTTP 핸들러와 stdin/stdout IPC가 공유. `--mode http|ipc` 플래그. |
| **배치 삽입** | `pgx.Batch`로 1000건씩 청크 INSERT. COPY보다 JSONB 타입 호환성 좋음. |

## 마스터 프롬프트 (AI 복원용)

```
당신은 숙련된 Go + React 풀스택 개발자입니다.
Amazon 셀러 리포트 데이터 허브 'Report Hub'를 구축해주세요.

기술 스택:
- Backend: Go 1.24, go-chi/chi (라우터), jackc/pgx (PostgreSQL), excelize (XLSX)
- Frontend: React 19 + TypeScript + Vite + Tailwind CSS v4
- Database: PostgreSQL (JSONB 스키마리스)
- 배포: fergusstrange/embedded-postgres + go:embed (단일 바이너리)

DB 스키마:
- rows: id, batch_id, report_type, channel, account, source, file_name, data(JSONB)
- batches: id, ts, report_type, source, account, file_name, total_rows, channel_counts(JSONB)
- config: key, value(JSONB)
- sync_log: id, ts, status, message, detail(JSONB)

핵심 기능:
1. 5가지 리포트 타입 통합 (transactions, inventory_ledger, top_search_terms, search_catalogue, sales_report)
2. CSV/TSV/XLSX 업로드 + 채널 자동 감지 (US FBA / CA FBA)
3. JSONB 검색/필터/페이지네이션
4. Embedded PostgreSQL (설치 불필요)
5. go:embed로 React SPA 바이너리 내장
6. HTTP REST API + stdin/stdout IPC 양방향
7. exe 더블클릭 → PG 자동 시작 → 브라우저 자동 오픈
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 amazon-report-hub 레퍼런스를 보고
"데이터 리포트 허브"를 만들어줘.
Go(chi) + React19 + Vite + TailwindV4 + PostgreSQL(JSONB) + embedded-postgres + go:embed.
스키마리스 JSONB 저장 + CSV/XLSX 업로드 + 단일 바이너리 배포.
```
