"""Playbook MCP Server - Claude Code용 플레이북 도구 서버"""

from pathlib import Path
from mcp.server.fastmcp import FastMCP

PLAYBOOK_DIR = Path(__file__).resolve().parent.parent
BLOCKED_FILES = {"_secrets.md"}

mcp = FastMCP("playbook")


def _read_md(path: Path) -> str | None:
    """Read a markdown file, returning None if blocked or missing."""
    if path.name in BLOCKED_FILES:
        return None
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _extract_desc(text: str) -> str:
    """Extract first blockquote line as description."""
    for line in text.splitlines():
        if line.startswith("> "):
            return line[2:].strip()
    return ""


def _extract_title(text: str) -> str:
    """Extract first heading as title."""
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _list_dir(subdir: str, label: str) -> list[dict]:
    """List markdown files in a subdirectory with title and description."""
    folder = PLAYBOOK_DIR / subdir
    if not folder.is_dir():
        return []
    items = []
    for f in sorted(folder.glob("*.md")):
        if f.name in BLOCKED_FILES or f.name == "README.md":
            continue
        text = f.read_text(encoding="utf-8")
        items.append({
            "name": f.stem,
            "type": label,
            "title": _extract_title(text),
            "description": _extract_desc(text),
        })
    return items


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
        items = _list_dir(subdir, label)
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
    content = _read_md(PLAYBOOK_DIR / "catalog" / f"{name}.md")
    if content is None:
        available = [f.stem for f in (PLAYBOOK_DIR / "catalog").glob("*.md")
                     if f.name not in BLOCKED_FILES and f.name != "README.md"]
        return f"모듈 '{name}'을 찾을 수 없습니다. 사용 가능: {', '.join(sorted(available))}"
    return content


@mcp.tool()
def get_reference(name: str) -> str:
    """레퍼런스(완성 프로젝트) 파일을 반환합니다. name은 파일명(확장자 제외). 예: pong, salary, mz"""
    content = _read_md(PLAYBOOK_DIR / "references" / f"{name}.md")
    if content is None:
        available = [f.stem for f in (PLAYBOOK_DIR / "references").glob("*.md")
                     if f.name not in BLOCKED_FILES and f.name != "README.md"]
        return f"레퍼런스 '{name}'을 찾을 수 없습니다. 사용 가능: {', '.join(sorted(available))}"
    return content


@mcp.tool()
def get_recipe(name: str) -> str:
    """레시피(구현 가이드) 파일을 반환합니다. name은 파일명(확장자 제외). 예: flask-dashboard"""
    content = _read_md(PLAYBOOK_DIR / "recipes" / f"{name}.md")
    if content is None:
        available = [f.stem for f in (PLAYBOOK_DIR / "recipes").glob("*.md")
                     if f.name not in BLOCKED_FILES and f.name != "README.md"]
        return f"레시피 '{name}'를 찾을 수 없습니다. 사용 가능: {', '.join(sorted(available))}"
    return content


@mcp.tool()
def get_gotcha(name: str) -> str:
    """삽질방지 가이드 파일을 반환합니다. name은 파일명(확장자 제외). 예: tailwind-v4, css-overflow"""
    content = _read_md(PLAYBOOK_DIR / "gotchas" / f"{name}.md")
    if content is None:
        available = [f.stem for f in (PLAYBOOK_DIR / "gotchas").glob("*.md")
                     if f.name not in BLOCKED_FILES and f.name != "README.md"]
        return f"삽질방지 '{name}'를 찾을 수 없습니다. 사용 가능: {', '.join(sorted(available))}"
    return content


@mcp.tool()
def search(query: str) -> str:
    """플레이북 전체 .md 파일에서 키워드 검색. 매칭된 파일과 해당 라인을 반환합니다."""
    query_lower = query.lower()
    results = []
    for md_file in sorted(PLAYBOOK_DIR.rglob("*.md")):
        if md_file.name in BLOCKED_FILES:
            continue
        # Skip .git and mcp-server directories
        rel = md_file.relative_to(PLAYBOOK_DIR)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if "mcp-server" in rel.parts:
            continue
        try:
            text = md_file.read_text(encoding="utf-8")
        except Exception:
            continue
        matches = []
        for i, line in enumerate(text.splitlines(), 1):
            if query_lower in line.lower():
                matches.append(f"  L{i}: {line.strip()}")
        if matches:
            results.append(f"**{rel.as_posix()}**\n" + "\n".join(matches[:5]))
            if len(matches) > 5:
                results[-1] += f"\n  ... (+{len(matches) - 5}건)"
    if not results:
        return f"'{query}'에 대한 검색 결과가 없습니다."
    return f"검색: '{query}' → {len(results)}개 파일 매칭\n\n" + "\n\n".join(results)


@mcp.tool()
def get_tech_map() -> str:
    """tech-map.md (기술 전체 지도)를 반환합니다."""
    content = _read_md(PLAYBOOK_DIR / "tech-map.md")
    if content is None:
        return "tech-map.md를 찾을 수 없습니다."
    return content


if __name__ == "__main__":
    mcp.run()
