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

## 설치

### 1. mcp 패키지 설치

```bash
pip install mcp
```

### 2. Claude Code 설정에 등록

`~/.claude/settings.json`의 `mcpServers`에 추가:

```json
{
  "mcpServers": {
    "playbook": {
      "command": "python",
      "args": ["C:\\Users\\ganna\\Downloads\\playbook\\mcp-server\\server.py"]
    }
  }
}
```

### 3. Claude Code 재시작

```bash
# 재시작 후 확인
/mcp
# → playbook 서버가 connected 상태인지 확인
```

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

## 사용 시나리오

### 새 프로젝트 시작 시

```
1. list_items()         ← 어떤 모듈이 있는지 파악
2. get_tech_map()       ← 기술 조합 확인
3. get_module("base")   ← 필요한 모듈만 조회
4. get_reference("pong") ← 비슷한 레퍼런스 참고
```

### 특정 기술 찾을 때

```
1. search("Redis")          ← 키워드로 검색
2. get_module("redis")      ← 매칭된 모듈 조회
```

### 삽질 해결할 때

```
1. search("overflow")           ← 증상 키워드 검색
2. get_gotcha("css-overflow")   ← 해결 가이드 조회
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
