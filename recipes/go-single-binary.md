# Go 단일 바이너리 배포

> go:embed + embedded-postgres로 exe 하나에 DB + 프론트엔드 + API 전부 내장.
> 더블클릭 한 번이면 PostgreSQL 자동 시작 → 브라우저 자동 오픈.

## 언제 쓰나?

- 비개발자에게 exe 하나만 보내서 바로 쓰게 하고 싶을 때
- PostgreSQL 설치 없이 JSONB 쿼리가 필요할 때
- React SPA + REST API를 단일 바이너리로 배포할 때

## 기술 스택

```
Go 1.24 + chi(라우터) + pgx(PostgreSQL) + excelize(XLSX)
+ fergusstrange/embedded-postgres + go:embed
+ React 19 + Vite + Tailwind CSS v4
```

## 핵심 패턴

### 1. go:embed로 React SPA 내장

```go
//go:embed frontend/dist/*
var frontendFS embed.FS

// 라우터에서 SPA 서빙
staticFS, _ := fs.Sub(frontendFS, "frontend/dist")
```

**SPA fallback** — API가 아닌 경로는 `index.html`로 폴백:

```go
func spaHandler(staticFS fs.FS) http.HandlerFunc {
    fileServer := http.FileServerFS(staticFS)
    return func(w http.ResponseWriter, r *http.Request) {
        // 파일이 있으면 그대로 서빙
        if f, err := fs.Stat(staticFS, strings.TrimPrefix(r.URL.Path, "/")); err == nil && !f.IsDir() {
            fileServer.ServeHTTP(w, r)
            return
        }
        // 없으면 index.html (SPA 라우팅)
        r.URL.Path = "/"
        fileServer.ServeHTTP(w, r)
    }
}
```

### 2. Embedded PostgreSQL

```go
import embeddedpostgres "github.com/fergusstrange/embedded-postgres"

pg := embeddedpostgres.NewDatabase(
    embeddedpostgres.DefaultConfig().
        Port(5433).
        DataPath(filepath.Join(dataDir, "pgdata")).
        RuntimePath(filepath.Join(dataDir, "pgruntime")).
        BinariesPath(filepath.Join(dataDir, "pgbin")).
        Database("myapp").
        Username("app").
        Password("app").
        StartTimeout(60 * time.Second),
)
pg.Start()
defer pg.Stop()
```

**데이터 디렉토리**: exe 옆 `.myapp/` 폴더에 PG 바이너리+데이터 저장.

```go
func dataPath() string {
    exe, _ := os.Executable()
    return filepath.Join(filepath.Dir(exe), ".myapp")
}
```

**첫 실행**: PG 바이너리를 인터넷에서 다운로드 후 캐시. 이후 오프라인 실행 가능.

### 3. JSONB 스키마리스 저장

서로 다른 컬럼 구조의 데이터를 하나의 테이블에 통합:

```sql
CREATE TABLE rows (
    id          SERIAL PRIMARY KEY,
    batch_id    TEXT NOT NULL,
    report_type TEXT NOT NULL,
    channel     TEXT,
    data        JSONB NOT NULL
);
CREATE INDEX idx_data_gin ON rows USING GIN(data);
```

검색: `data::text ILIKE '%검색어%'` + GIN 인덱스로 JSON 경로 쿼리.

### 4. pgx.Batch 벌크 삽입

COPY 대신 Batch 사용 (JSONB 타입 호환성):

```go
const chunkSize = 1000
batch := &pgx.Batch{}
for _, row := range rows {
    batch.Queue("INSERT INTO rows (...) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)",
        row.BatchID, row.ReportType, ...)
    if batch.Len() >= chunkSize {
        br := s.Pool.SendBatch(ctx, batch)
        br.Close()
        batch = &pgx.Batch{}
    }
}
```

### 5. 듀얼 모드 (HTTP / IPC)

같은 Store 레이어를 HTTP와 stdin/stdout IPC가 공유:

```go
switch *mode {
case "http":
    http.ListenAndServe(addr, api.NewRouter(s, staticFS))
case "ipc":
    ipc.Run(os.Stdin, os.Stdout, s)
}
```

IPC 모드: `--mode ipc`로 실행하면 Electron 앱에서 stdin/stdout JSON-line으로 통신.

### 6. 자동 브라우저 오픈

```go
func openBrowser(url string) {
    switch runtime.GOOS {
    case "windows":
        exec.Command("cmd", "/c", "start", url).Start()
    case "darwin":
        exec.Command("open", url).Start()
    default:
        exec.Command("xdg-open", url).Start()
    }
}
```

## 빌드 순서

```bash
# 1. 프론트엔드 빌드
cd frontend && npm run build && cd ..

# 2. Go 바이너리 빌드
go build -o myapp.exe .

# 3. 실행 (자동으로 PG 시작 + 브라우저 오픈)
./myapp.exe
./myapp.exe --seed        # mock 데이터 포함
./myapp.exe --mode ipc    # Electron IPC 모드
```

## Graceful Shutdown

```go
sigCh := make(chan os.Signal, 1)
signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
go func() {
    <-sigCh
    pg.Stop()
    os.Exit(0)
}()
defer pg.Stop()
```

## 주의사항

- **첫 실행 시 인터넷 필요** — embedded-postgres가 PG 바이너리를 다운로드
- **포트 충돌** — PG 기본 5432 대신 5433 사용 권장
- **Windows 방화벽** — 첫 실행 시 방화벽 허용 팝업 발생 가능
- **ensureDB 실패** — embedded PG가 DB를 미리 생성하므로 non-fatal 처리

## 레퍼런스

- [amazon-report-hub](references/amazon-report-hub.md) — 이 패턴의 실제 구현
- [dictionary](references/dictionary.md) — Go + go:embed 단일 바이너리 (MySQL 버전)
