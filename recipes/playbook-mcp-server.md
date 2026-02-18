# Playbook MCP Server 사용법

> Claude Code에서 플레이북을 MCP 도구로 조회하는 방법.
> 매번 파일을 Read하지 않아 토큰을 대폭 절감.

## 개요

MCP(Model Context Protocol) 서버를 통해 Claude가 플레이북 내용을 **도구 호출**로 가져옴.
전체 파일을 Read하는 대신, 필요한 모듈/레퍼런스/레시피만 정확히 조회.

| 항목 | 내용 |
|------|------|
| **위치** | `mcp-server/server.py` |
| **프레임워크** | Python FastMCP (`mcp` 패키지) |
| **통신** | stdio (Claude Code 표준) |
| **보안** | `_secrets.md` 자동 차단 |

## 새 PC에서 설치하기 (복붙용)

### Step 1: uv 설치 (Python 패키지 실행 도구)

```bash
pip install uv
```

> 이미 있으면 스킵.

### Step 2: settings.json에 붙여넣기

Claude Code 설정 파일을 연다:

- **Windows**: `C:\Users\{유저명}\.claude\settings.json`
- **Mac/Linux**: `~/.claude/settings.json`

`mcpServers` 안에 아래를 붙여넣기:

```json
"playbook": {
  "command": "uvx",
  "args": ["playbook-mcp"]
}
```

전체 예시 (다른 MCP 서버가 없는 경우):

```json
{
  "mcpServers": {
    "playbook": {
      "command": "uvx",
      "args": ["playbook-mcp"]
    }
  }
}
```

### Step 3: Claude Code 재시작 → 확인

```bash
/mcp
# → playbook 서버가 connected 상태면 성공
```

끝. `uvx`가 PyPI에서 자동으로 다운로드 → 설치 → 실행합니다.
로컬에 playbook 파일 없어도 됨. 데이터는 GitHub에서 가져옴.

> `_secrets.md`는 자동 차단됨.

## 도구 목록 (7개)

### `list_items()`

플레이북 전체 목록을 이름 + 한줄 설명으로 반환.
새 대화 시작할 때 **이것만 호출하면 전체 파악 가능**.

```
→ ~200토큰으로 모듈 30개 + 레퍼런스 + 레시피 + 삽질방지 전체 목록
```

### `get_module(name)`

모듈 카탈로그 1개 조회. `name`은 파일명(확장자 제외).

```
get_module("quiz")    → catalog/quiz.md
get_module("base")    → catalog/base.md
get_module("radar")   → catalog/radar.md
```

### `get_reference(name)`

레퍼런스(완성 프로젝트) 1개 조회.

```
get_reference("pong")     → references/pong.md
get_reference("salary")   → references/salary.md
```

### `get_recipe(name)`

레시피(구현 가이드) 1개 조회.

```
get_recipe("flask-dashboard")      → recipes/flask-dashboard.md
get_recipe("react-vite-tailwind")  → recipes/react-vite-tailwind.md
```

### `get_gotcha(name)`

삽질방지 가이드 1개 조회.

```
get_gotcha("tailwind-v4")   → gotchas/tailwind-v4.md
get_gotcha("css-overflow")  → gotchas/css-overflow.md
```

### `search(query)`

전체 `.md` 파일에서 키워드 검색. 매칭 파일과 해당 라인을 반환.

```
search("Tailwind")   → 20개 파일에서 Tailwind 언급 라인
search("카카오")      → 카카오 관련 파일 + 라인
search("Django")     → Django 관련 모든 매칭
```

### `get_tech_map()`

`tech-map.md` 전체 반환. 모든 기술이 어디에 쓰이는지 한눈에.

## 이렇게 말하면 됩니다

MCP 도구는 **별도 명령어 없이 자연어로 요청**하면 Claude가 알아서 호출합니다.

### 전체 목록 보기 → `list_items()`

```
"플레이북 뭐 있어?"
"모듈 목록 보여줘"
"어떤 레퍼런스가 있지?"
"플레이북 전체 목록"
```

### 모듈 조회 → `get_module(name)`

```
"QUIZ 모듈 보여줘"
"BASE 모듈 어떻게 생겼어?"
"레이더 차트 모듈 가져와"
"카카오 공유 모듈 참고해줘"
```

### 레퍼런스 조회 → `get_reference(name)`

```
"pong 레퍼런스 보여줘"
"pong이랑 비슷하게 만들어줘"
"salary 프로젝트 구조 참고해"
"hexalounge는 어떻게 만들었어?"
```

### 레시피 조회 → `get_recipe(name)`

```
"Flask 대시보드 레시피 보여줘"
"React+Vite+Tailwind 세팅 방법"
"Django HTMX 레시피 참고해줘"
"서버에서 GitHub 올리는 법"
```

### 삽질방지 조회 → `get_gotcha(name)`

```
"Tailwind 삽질 뭐 있었지?"
"CSS 오버플로우 해결법"
"EC2 OOM 문제 어떻게 해결해?"
"Cloudflare 배포 삽질 방지"
```

### 키워드 검색 → `search(query)`

```
"플레이북에서 Redis 관련 내용 찾아줘"
"카카오 관련 모듈이 뭐가 있어?"
"Django 쓰는 프로젝트 어떤 게 있지?"
"Tailwind가 어디어디에서 쓰이는지 찾아봐"
```

### 기술 지도 → `get_tech_map()`

```
"기술 지도 보여줘"
"어떤 기술이 어디에 쓰이는지 한눈에 보고 싶어"
"tech-map 불러와"
```

## 사용 시나리오

### 새 프로젝트 시작 시

> "바이럴 테스트 앱 만들어줘"

Claude가 알아서 이 순서로 호출:
```
1. list_items()          ← 어떤 모듈이 있는지 파악
2. get_tech_map()        ← 기술 조합 확인
3. get_module("base")    ← 필요한 모듈만 조회
4. get_reference("pong") ← 비슷한 레퍼런스 참고
```

### 기존 프로젝트 참고할 때

> "pong이랑 비슷하게 만들어줘"

```
1. get_reference("pong")  ← pong 구조 파악
2. get_module("quiz")     ← 퀴즈 엔진 참고
3. get_module("grade")    ← 등급 시스템 참고
```

### 특정 기술 찾을 때

> "Redis 캐싱 어떻게 하는지 알려줘"

```
1. search("Redis")        ← 키워드로 검색
2. get_module("redis")    ← 매칭된 모듈 조회
```

### 삽질 해결할 때

> "Tailwind 패딩이 안 먹혀"

```
1. search("overflow")           ← 증상 키워드 검색
2. get_gotcha("tailwind-v4")    ← 해결 가이드 조회
```

## 토큰 절감 효과

| 방식 | 토큰 소비 |
|------|----------|
| 파일 전체 Read | ~5,000+ / 파일 |
| `list_items()` | ~200 (전체 목록) |
| `get_module()` 1개 | ~500 (해당 파일만) |
| `search()` | ~300 (매칭 라인만) |

**INSTRUCTIONS.md 전체 Read 대비 90%+ 절감**.

## 서버 구조

```
mcp-server/
├── server.py          ← FastMCP 서버 (단일 파일, 7개 도구)
└── requirements.txt   ← mcp>=1.0.0
```

## 새 파일 추가 시

플레이북에 새 md 파일을 추가하면 **서버 수정 없이 자동 반영**.
디렉토리 기반으로 파일을 스캔하기 때문.

- `catalog/xxx.md` 추가 → `get_module("xxx")` 바로 사용 가능
- `references/xxx.md` 추가 → `get_reference("xxx")` 바로 사용 가능
- `recipes/xxx.md` 추가 → `get_recipe("xxx")` 바로 사용 가능
- `gotchas/xxx.md` 추가 → `get_gotcha("xxx")` 바로 사용 가능
