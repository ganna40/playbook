"""Playbook MCP Server - GitHub에서 플레이북을 직접 가져오는 MCP 서버"""

import time
import httpx
from mcp.server.fastmcp import FastMCP

REPO = "ganna40/playbook"
BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"
API_BASE = f"https://api.github.com/repos/{REPO}/contents"
BLOCKED_FILES = {"_secrets.md"}
CACHE_TTL = 300  # 5분 캐시

mcp = FastMCP("playbook")

# ── 캐시 ───────────────────────────────────────────────
_cache: dict[str, tuple[float, str | list]] = {}


def _cached_get(key: str, fetcher):
    """TTL 기반 캐시. 5분간 동일 요청 재사용."""
    now = time.time()
    if key in _cache and now - _cache[key][0] < CACHE_TTL:
        return _cache[key][1]
    result = fetcher()
    _cache[key] = (now, result)
    return result


# ── GitHub 통신 ────────────────────────────────────────
def _fetch_raw(path: str) -> str | None:
    """GitHub raw 파일 가져오기."""
    filename = path.rsplit("/", 1)[-1] if "/" in path else path
    if filename in BLOCKED_FILES:
        return None

    def fetch():
        r = httpx.get(f"{RAW_BASE}/{path}", timeout=10, follow_redirects=True)
        if r.status_code == 200:
            return r.text
        return None

    return _cached_get(f"raw:{path}", fetch)


def _list_github_dir(subdir: str) -> list[dict]:
    """GitHub API로 디렉토리 내 md 파일 목록 조회."""
    def fetch():
        r = httpx.get(f"{API_BASE}/{subdir}", timeout=10, follow_redirects=True)
        if r.status_code != 200:
            return []
        return [
            item["name"] for item in r.json()
            if item["name"].endswith(".md")
            and item["name"] not in BLOCKED_FILES
            and item["name"] != "README.md"
        ]

    return _cached_get(f"dir:{subdir}", fetch)


# ── 유틸 ──────────────────────────────────────────────
def _extract_title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _extract_desc(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("> "):
            return line[2:].strip()
    return ""


def _list_section(subdir: str, label: str) -> list[dict]:
    """섹션 내 모든 md 파일의 이름/제목/설명 목록."""
    files = _list_github_dir(subdir)
    items = []
    for fname in sorted(files):
        text = _fetch_raw(f"{subdir}/{fname}")
        if text is None:
            continue
        stem = fname.removesuffix(".md")
        items.append({
            "name": stem,
            "type": label,
            "title": _extract_title(text),
            "description": _extract_desc(text),
        })
    return items


def _get_file(subdir: str, name: str, label: str) -> str:
    """특정 섹션에서 파일 1개를 가져오거나 사용 가능 목록을 반환."""
    content = _fetch_raw(f"{subdir}/{name}.md")
    if content is not None:
        return content
    available = [f.removesuffix(".md") for f in _list_github_dir(subdir)]
    return f"{label} '{name}'을(를) 찾을 수 없습니다. 사용 가능: {', '.join(sorted(available))}"


# ── Tools ──────────────────────────────────────────────

@mcp.tool()
def list_items() -> str:
    """플레이북 전체 목록을 반환합니다 (모듈/레퍼런스/레시피/삽질방지).
    각 항목의 이름, 타입, 제목, 한줄 설명을 포함합니다."""
    sections = [
        ("catalog", "module"),
        ("references", "reference"),
        ("recipes", "recipe"),
        ("gotchas", "gotcha"),
        ("templates", "template"),
    ]
    lines = []
    for subdir, label in sections:
        items = _list_section(subdir, label)
        if not items:
            continue
        lines.append(f"\n## {label.upper()} ({len(items)}개)")
        for item in items:
            desc = f" - {item['description']}" if item["description"] else ""
            lines.append(f"- **{item['name']}**: {item['title']}{desc}")
    return "\n".join(lines).strip()


@mcp.tool()
def get_module(name: str) -> str:
    """모듈 카탈로그 파일을 반환합니다. name은 파일명(확장자 제외). 예: quiz, base, data"""
    return _get_file("catalog", name, "모듈")


@mcp.tool()
def get_reference(name: str) -> str:
    """레퍼런스(완성 프로젝트) 파일을 반환합니다. name은 파일명(확장자 제외). 예: pong, salary, mz"""
    return _get_file("references", name, "레퍼런스")


@mcp.tool()
def get_recipe(name: str) -> str:
    """레시피(구현 가이드) 파일을 반환합니다. name은 파일명(확장자 제외). 예: flask-dashboard"""
    return _get_file("recipes", name, "레시피")


@mcp.tool()
def get_gotcha(name: str) -> str:
    """삽질방지 가이드 파일을 반환합니다. name은 파일명(확장자 제외). 예: tailwind-v4, css-overflow"""
    return _get_file("gotchas", name, "삽질방지")


@mcp.tool()
def search(query: str) -> str:
    """플레이북 전체 .md 파일에서 키워드 검색. 매칭된 파일과 해당 라인을 반환합니다."""
    query_lower = query.lower()
    results = []
    dirs = ["catalog", "references", "recipes", "gotchas", "templates"]
    for subdir in dirs:
        files = _list_github_dir(subdir)
        for fname in sorted(files):
            text = _fetch_raw(f"{subdir}/{fname}")
            if text is None:
                continue
            matches = []
            for i, line in enumerate(text.splitlines(), 1):
                if query_lower in line.lower():
                    matches.append(f"  L{i}: {line.strip()}")
            if matches:
                results.append(f"**{subdir}/{fname}**\n" + "\n".join(matches[:5]))
                if len(matches) > 5:
                    results[-1] += f"\n  ... (+{len(matches) - 5}건)"

    # 루트 파일도 검색 (tech-map, builder, INSTRUCTIONS 등)
    for root_file in ["tech-map.md", "builder.md", "INSTRUCTIONS.md", "_sidebar.md"]:
        text = _fetch_raw(root_file)
        if text is None:
            continue
        matches = []
        for i, line in enumerate(text.splitlines(), 1):
            if query_lower in line.lower():
                matches.append(f"  L{i}: {line.strip()}")
        if matches:
            results.append(f"**{root_file}**\n" + "\n".join(matches[:5]))
            if len(matches) > 5:
                results[-1] += f"\n  ... (+{len(matches) - 5}건)"

    if not results:
        return f"'{query}'에 대한 검색 결과가 없습니다."
    return f"검색: '{query}' → {len(results)}개 파일 매칭\n\n" + "\n\n".join(results)


@mcp.tool()
def get_tech_map() -> str:
    """tech-map.md (기술 전체 지도)를 반환합니다."""
    content = _fetch_raw("tech-map.md")
    if content is None:
        return "tech-map.md를 찾을 수 없습니다."
    return content


def main():
    mcp.run()


if __name__ == "__main__":
    main()
