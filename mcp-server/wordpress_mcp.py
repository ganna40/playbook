"""WordPress SEO MCP Server — pearsoninsight.com 전용

Claude Code에서 "이 주제로 글 써줘" 한마디로:
1. 키워드 리서치 → 2. SEO 글 작성 → 3. draft 업로드 → 4. 리뷰 → 5. 예약 발행

파이프라인: draft → review → schedule
"""

import base64
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# .env 파일 로드 (서버 파일과 같은 디렉토리)
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

# ── 설정 ────────────────────────────────────────────────
WP_URL = os.environ.get("WP_URL", "https://pearsoninsight.com")
WP_USERNAME = os.environ.get("WP_USERNAME", "")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD", "")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")

API_BASE = f"{WP_URL}/wp-json/wp/v2"
RANKMATH_API = f"{WP_URL}/wp-json/rankmath/v1"
TIMEOUT = 30

mcp = FastMCP("wordpress")

# ── 인증 헬퍼 ──────────────────────────────────────────
def _auth_header() -> dict:
    """Basic Auth 헤더 생성."""
    if not WP_USERNAME or not WP_APP_PASSWORD:
        return {}
    token = base64.b64encode(f"{WP_USERNAME}:{WP_APP_PASSWORD}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def _wp_get(endpoint: str, params: dict | None = None) -> httpx.Response:
    """WordPress REST API GET 요청."""
    url = f"{API_BASE}/{endpoint}" if not endpoint.startswith("http") else endpoint
    return httpx.get(url, headers=_auth_header(), params=params or {}, timeout=TIMEOUT, follow_redirects=True)


def _wp_post(endpoint: str, json_data: dict | None = None, **kwargs) -> httpx.Response:
    """WordPress REST API POST 요청."""
    url = f"{API_BASE}/{endpoint}" if not endpoint.startswith("http") else endpoint
    headers = {**_auth_header(), "Content-Type": "application/json"}
    if json_data is not None:
        return httpx.post(url, headers=headers, json=json_data, timeout=TIMEOUT, follow_redirects=True)
    return httpx.post(url, headers={**_auth_header(), **kwargs.get("headers", {})},
                      content=kwargs.get("content"), timeout=TIMEOUT, follow_redirects=True)


# ── 카테고리/태그 이름→ID 변환 ──────────────────────────
_cat_cache: dict[str, int] = {}
_tag_cache: dict[str, int] = {}


def _resolve_category(name: str) -> int | None:
    """카테고리 이름 → ID. 없으면 None."""
    name_lower = name.lower().strip()
    if name_lower in _cat_cache:
        return _cat_cache[name_lower]
    try:
        r = _wp_get("categories", {"per_page": 100, "search": name})
        if r.status_code == 200:
            for cat in r.json():
                _cat_cache[cat["name"].lower().strip()] = cat["id"]
                if cat["name"].lower().strip() == name_lower or cat["slug"] == name_lower:
                    return cat["id"]
    except Exception:
        pass
    return None


def _resolve_or_create_tag(name: str) -> int | None:
    """태그 이름 → ID. 없으면 생성."""
    name_stripped = name.strip()
    name_lower = name_stripped.lower()
    if name_lower in _tag_cache:
        return _tag_cache[name_lower]
    try:
        r = _wp_get("tags", {"per_page": 100, "search": name_stripped})
        if r.status_code == 200:
            for tag in r.json():
                _tag_cache[tag["name"].lower().strip()] = tag["id"]
                if tag["name"].lower().strip() == name_lower:
                    return tag["id"]
        # 없으면 생성
        r = _wp_post("tags", {"name": name_stripped})
        if r.status_code in (200, 201):
            tag_id = r.json()["id"]
            _tag_cache[name_lower] = tag_id
            return tag_id
    except Exception:
        pass
    return None


def _resolve_tags(names: list[str]) -> list[int]:
    """태그 이름 리스트 → ID 리스트."""
    ids = []
    for name in names:
        tid = _resolve_or_create_tag(name)
        if tid:
            ids.append(tid)
    return ids


# ── 슬러그 자동 생성 ─────────────────────────────────────

def _keyword_to_slug(keyword: str) -> str:
    """포커스 키워드에서 URL 슬러그 자동 생성.
    영문은 소문자, 한글은 유지, 공백은 하이픈으로."""
    slug = keyword.lower().strip()
    # 영문+숫자+한글+하이픈만 유지
    slug = re.sub(r'[^\w가-힣\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = slug.strip('-')
    return slug


# ── RankMath 메타 설정 ───────────────────────────────────

def _set_rankmath_meta(post_id: int, focus_keyword: str = "", seo_title: str = "", meta_description: str = "") -> str | None:
    """RankMath API로 SEO 메타 필드를 설정합니다. 성공 시 None, 실패 시 에러 메시지."""
    meta = {}
    if focus_keyword:
        meta["rank_math_focus_keyword"] = focus_keyword
    if seo_title:
        meta["rank_math_title"] = seo_title
    if meta_description:
        meta["rank_math_description"] = meta_description
    if not meta:
        return None
    try:
        r = httpx.post(
            f"{RANKMATH_API}/updateMeta",
            headers={**_auth_header(), "Content-Type": "application/json"},
            json={"objectType": "post", "objectID": post_id, "meta": meta},
            timeout=TIMEOUT,
            follow_redirects=True,
        )
        if r.status_code == 200:
            # 로컬 캐시 업데이트
            if post_id not in _rankmath_cache:
                _rankmath_cache[post_id] = {}
            _rankmath_cache[post_id].update(meta)
            return None
        return f"RankMath 메타 설정 실패: HTTP {r.status_code}"
    except Exception as e:
        return f"RankMath 메타 설정 실패: {e}"


# 로컬 캐시: RankMath 메타를 REST API에서 읽을 수 없으므로, 쓸 때 캐시해둠
_rankmath_cache: dict[int, dict] = {}


def _get_rankmath_meta(post_id: int) -> dict:
    """RankMath 메타 필드를 가져옵니다. 로컬 캐시에서 조회."""
    return _rankmath_cache.get(post_id, {})


def _compute_seo_score(post_id: int) -> dict | None:
    """서버사이드 SEO 점수 계산 (custom REST endpoint).
    점수를 계산하고 rank_math_seo_score에 저장합니다."""
    try:
        r = httpx.get(
            f"{WP_URL}/wp-json/custom/v1/seo-score/{post_id}",
            headers=_auth_header(),
            timeout=TIMEOUT,
            follow_redirects=True,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


# ── 도구 1: 연결 확인 ────────────────────────────────────

@mcp.tool()
def wp_check_connection() -> str:
    """WordPress 연결 + 인증 + RankMath API 상태를 확인합니다."""
    results = []

    # 1. 사이트 접속
    try:
        r = httpx.get(f"{WP_URL}/wp-json/", timeout=TIMEOUT, follow_redirects=True)
        if r.status_code == 200:
            data = r.json()
            results.append(f"✅ 사이트: {data.get('name', WP_URL)}")
            namespaces = data.get("namespaces", [])
            has_rankmath = any(ns.startswith("rankmath") for ns in namespaces)
            results.append(f"✅ RankMath API: {'활성화' if has_rankmath else '❌ 비활성화'}")
        else:
            results.append(f"❌ 사이트 접속 실패: HTTP {r.status_code}")
            return "\n".join(results)
    except Exception as e:
        return f"❌ 사이트 접속 실패: {e}"

    # 2. 인증
    if not WP_USERNAME or not WP_APP_PASSWORD:
        results.append("❌ 인증: WP_USERNAME / WP_APP_PASSWORD 환경변수 미설정")
    else:
        try:
            r = _wp_get("users/me")
            if r.status_code == 200:
                user = r.json()
                results.append(f"✅ 인증: {user.get('name', WP_USERNAME)} (ID: {user['id']})")
            else:
                results.append(f"❌ 인증 실패: HTTP {r.status_code}")
        except Exception as e:
            results.append(f"❌ 인증 실패: {e}")

    # 3. 카테고리 목록
    try:
        r = _wp_get("categories", {"per_page": 100})
        if r.status_code == 200:
            cats = r.json()
            cat_list = ", ".join(f"{c['name']}({c['id']})" for c in cats)
            results.append(f"📂 카테고리: {cat_list}")
    except Exception:
        pass

    # 4. 이미지 API 키
    results.append(f"🖼️ Unsplash: {'설정됨' if UNSPLASH_ACCESS_KEY else '미설정'}")
    results.append(f"🖼️ Pexels: {'설정됨' if PEXELS_API_KEY else '미설정'}")
    results.append(f"🖼️ Pixabay: {'설정됨' if PIXABAY_API_KEY else '미설정'}")

    return "\n".join(results)


# ── 도구 2: 키워드 리서치 ─────────────────────────────────

@mcp.tool()
def wp_keyword_research(topic: str) -> str:
    """주제에 대한 키워드 리서치를 수행합니다.
    Google 자동완성으로 실제 검색어를 수집하고,
    기존 글과의 중복 여부를 확인합니다.

    Args:
        topic: 리서치할 주제 (예: "AI 에이전트", "워드프레스 SEO")
    """
    results = {"topic": topic, "autocomplete": [], "competition_titles": [], "recommended_focus": "", "recommended_longtail": []}

    # 1. Google 자동완성
    try:
        r = httpx.get(
            "https://www.google.com/complete/search",
            params={"client": "chrome", "q": topic, "hl": "ko"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10, follow_redirects=True,
        )
        if r.status_code == 200:
            data = r.json()
            if len(data) > 1 and isinstance(data[1], list):
                results["autocomplete"] = data[1][:10]
    except Exception:
        pass

    # 2. 영문 자동완성도 시도 (롱테일 확장)
    try:
        r = httpx.get(
            "https://www.google.com/complete/search",
            params={"client": "chrome", "q": topic, "hl": "en"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10, follow_redirects=True,
        )
        if r.status_code == 200:
            data = r.json()
            if len(data) > 1 and isinstance(data[1], list):
                en_suggestions = [s for s in data[1][:5] if s not in results["autocomplete"]]
                results["autocomplete_en"] = en_suggestions
    except Exception:
        pass

    # 3. 키워드 추천
    if results["autocomplete"]:
        results["recommended_focus"] = topic
        results["recommended_longtail"] = results["autocomplete"][:5]

    # 4. 포맷팅
    lines = [f"## 키워드 리서치: {topic}\n"]
    lines.append("### Google 자동완성 (한국어)")
    for i, kw in enumerate(results["autocomplete"], 1):
        lines.append(f"  {i}. {kw}")

    if results.get("autocomplete_en"):
        lines.append("\n### Google 자동완성 (영어)")
        for i, kw in enumerate(results["autocomplete_en"], 1):
            lines.append(f"  {i}. {kw}")

    lines.append(f"\n### 추천")
    lines.append(f"- 포커스 키워드: **{results['recommended_focus']}**")
    lines.append(f"- 롱테일 후보: {', '.join(results['recommended_longtail'])}")
    lines.append(f"\n💡 WebSearch로 상위 글을 분석하고 경쟁도를 판단하세요.")
    lines.append(f"   예: WebSearch(\"{topic} 2026\"), WebSearch(\"{topic} site:tistory.com\")")

    return "\n".join(lines)


# ── 도구 3: 카니발리제이션 체크 ──────────────────────────

@mcp.tool()
def wp_check_cannibalization(focus_keyword: str) -> str:
    """기존 글 중 동일 키워드를 타겟하는 글이 있는지 확인합니다.

    Args:
        focus_keyword: 체크할 포커스 키워드
    """
    kw_lower = focus_keyword.lower()
    conflicts = []

    try:
        # 키워드로 검색 (publish만 공개 API로 검색, draft/future는 인증 필요)
        r = _wp_get("posts", {"per_page": 50, "search": focus_keyword, "status": "publish"})
        if r.status_code == 200:
            for post in r.json():
                title = post["title"]["rendered"]
                slug = post["slug"]
                # 제목이나 슬러그에 키워드 포함 여부
                if kw_lower in title.lower() or kw_lower.replace(" ", "-") in slug:
                    conflicts.append({
                        "id": post["id"],
                        "title": title,
                        "slug": slug,
                        "status": post["status"],
                        "url": post["link"],
                    })
    except Exception as e:
        return f"❌ 체크 실패: {e}"

    if not conflicts:
        return f"✅ '{focus_keyword}' 관련 기존 글 없음 — 새 글 작성 가능"

    lines = [f"⚠️ '{focus_keyword}' 관련 기존 글 {len(conflicts)}개 발견:\n"]
    for c in conflicts:
        lines.append(f"- [{c['status']}] {c['title']}")
        lines.append(f"  URL: {c['url']}")
        lines.append(f"  ID: {c['id']}")
    lines.append(f"\n💡 기존 글을 업데이트하거나, 다른 롱테일 키워드로 분리하세요.")
    return "\n".join(lines)


# ── 도구 4: 글 생성 ──────────────────────────────────────

@mcp.tool()
def wp_create_post(
    title: str,
    content: str,
    focus_keyword: str = "",
    seo_title: str = "",
    meta_description: str = "",
    slug: str = "",
    excerpt: str = "",
    category: str = "",
    tags: str = "",
    featured_media_id: int = 0,
    status: str = "draft",
    publish_date: str = "",
) -> str:
    """WordPress에 새 글을 생성합니다.

    Args:
        title: 글 제목
        content: HTML 본문
        focus_keyword: RankMath 포커스 키워드
        seo_title: RankMath SEO 제목 (비면 title 사용)
        meta_description: RankMath 메타 설명
        slug: URL 슬러그 (빈값이면 자동 생성)
        excerpt: 요약문 (80~120자)
        category: 카테고리 이름 (예: "테크", "AI")
        tags: 쉼표로 구분된 태그 (예: "AI 요약,LLM,프롬프트")
        featured_media_id: 대표 이미지 미디어 ID (0이면 없음)
        status: draft(기본), future(예약), publish(즉시)
        publish_date: 예약 발행 시간 (ISO 8601, 예: "2026-02-20T09:00:00")
    """
    post_data: dict = {
        "title": title,
        "content": content,
        "status": status,
    }

    # 슬러그 (포커스 키워드 기반 자동 생성)
    if slug:
        post_data["slug"] = slug
    elif focus_keyword:
        post_data["slug"] = _keyword_to_slug(focus_keyword)

    # 요약문
    if excerpt:
        post_data["excerpt"] = excerpt

    # 카테고리
    if category:
        cat_id = _resolve_category(category)
        if cat_id:
            post_data["categories"] = [cat_id]

    # 태그
    if tags:
        tag_names = [t.strip() for t in tags.split(",") if t.strip()]
        tag_ids = _resolve_tags(tag_names)
        if tag_ids:
            post_data["tags"] = tag_ids

    # 대표 이미지
    if featured_media_id:
        post_data["featured_media"] = featured_media_id

    # 예약 발행
    if publish_date:
        post_data["date"] = publish_date
        if status == "draft":
            post_data["status"] = "future"

    try:
        r = _wp_post("posts", post_data)
        if r.status_code in (200, 201):
            post = r.json()
            lines = [
                f"✅ 글 생성 완료",
                f"- ID: {post['id']}",
                f"- 제목: {post['title']['rendered']}",
                f"- 상태: {post['status']}",
                f"- URL: {post['link']}",
                f"- 미리보기: {WP_URL}/?p={post['id']}&preview=true",
            ]
            if post["status"] == "future":
                lines.append(f"- 발행 예정: {post.get('date', publish_date)}")

            # RankMath SEO 메타 설정 (별도 API)
            rm_err = _set_rankmath_meta(post['id'], focus_keyword, seo_title, meta_description)
            if rm_err:
                lines.append(f"⚠️ {rm_err}")
            elif focus_keyword or seo_title or meta_description:
                lines.append(f"✅ RankMath SEO 메타 설정 완료")

            # 서버사이드 SEO 점수 자동 계산
            if focus_keyword:
                seo_data = _compute_seo_score(post['id'])
                if seo_data and 'score' in seo_data:
                    lines.append(f"- SEO 점수: {seo_data['score']}/100")

            return "\n".join(lines)
        else:
            error_body = r.text[:500]
            return f"❌ 글 생성 실패: HTTP {r.status_code}\n{error_body}"
    except Exception as e:
        return f"❌ 글 생성 실패: {e}"


# ── 도구 5: 글 수정 ──────────────────────────────────────

@mcp.tool()
def wp_update_post(
    post_id: int,
    title: str = "",
    content: str = "",
    focus_keyword: str = "",
    seo_title: str = "",
    meta_description: str = "",
    slug: str = "",
    excerpt: str = "",
    category: str = "",
    tags: str = "",
    featured_media_id: int = 0,
    status: str = "",
    publish_date: str = "",
) -> str:
    """기존 글을 수정합니다. 변경할 필드만 값을 넣으세요.

    Args:
        post_id: 수정할 글 ID
        title: 글 제목
        content: HTML 본문
        focus_keyword: RankMath 포커스 키워드
        seo_title: RankMath SEO 제목
        meta_description: RankMath 메타 설명
        slug: URL 슬러그
        excerpt: 요약문
        category: 카테고리 이름
        tags: 쉼표로 구분된 태그
        featured_media_id: 대표 이미지 미디어 ID
        status: draft, future, publish
        publish_date: 예약 발행 시간 (ISO 8601)
    """
    post_data: dict = {}

    if title:
        post_data["title"] = title
    if content:
        post_data["content"] = content
    if slug:
        post_data["slug"] = slug
    if excerpt:
        post_data["excerpt"] = excerpt
    if category:
        cat_id = _resolve_category(category)
        if cat_id:
            post_data["categories"] = [cat_id]
    if tags:
        tag_names = [t.strip() for t in tags.split(",") if t.strip()]
        tag_ids = _resolve_tags(tag_names)
        if tag_ids:
            post_data["tags"] = tag_ids
    if featured_media_id:
        post_data["featured_media"] = featured_media_id
    if status:
        post_data["status"] = status
    if publish_date:
        post_data["date"] = publish_date

    try:
        lines = []
        if post_data:
            r = _wp_post(f"posts/{post_id}", post_data)
            if r.status_code in (200, 201):
                post = r.json()
                lines.append(f"✅ 글 수정 완료 (ID: {post['id']}, 상태: {post['status']})")
            else:
                return f"❌ 글 수정 실패: HTTP {r.status_code}\n{r.text[:500]}"

        # RankMath SEO 메타 설정 (별도 API)
        rm_err = _set_rankmath_meta(post_id, focus_keyword, seo_title, meta_description)
        if rm_err:
            lines.append(f"⚠️ {rm_err}")
        elif focus_keyword or seo_title or meta_description:
            lines.append(f"✅ RankMath SEO 메타 설정 완료")

        # 서버사이드 SEO 점수 재계산
        seo_data = _compute_seo_score(post_id)
        if seo_data and 'score' in seo_data:
            lines.append(f"- SEO 점수: {seo_data['score']}/100")

        return "\n".join(lines) if lines else "변경사항 없음"
    except Exception as e:
        return f"❌ 글 수정 실패: {e}"


# ── 도구 6: 글 목록 ──────────────────────────────────────

@mcp.tool()
def wp_list_posts(count: int = 10, status: str = "publish") -> str:
    """최근 글 목록을 반환합니다.

    Args:
        count: 가져올 글 수 (기본 10)
        status: publish, draft, future, any (기본 publish)
    """
    params = {"per_page": min(count, 100), "orderby": "date", "order": "desc"}
    if status != "any":
        params["status"] = status

    try:
        r = _wp_get("posts", params)
        if r.status_code != 200:
            return f"❌ 글 목록 조회 실패: HTTP {r.status_code}"
        posts = r.json()
        if not posts:
            return f"글이 없습니다 (status={status})"

        lines = [f"## 최근 글 ({status}, {len(posts)}개)\n"]
        for p in posts:
            date_str = p.get("date", "")[:10]
            lines.append(f"- [{p['status']}] **{p['title']['rendered']}**")
            lines.append(f"  ID: {p['id']} | 날짜: {date_str} | {p['link']}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ 글 목록 조회 실패: {e}"


# ── 도구 7: 글 조회 ──────────────────────────────────────

@mcp.tool()
def wp_get_post(post_id: int) -> str:
    """특정 글의 상세 정보를 반환합니다 (HTML 본문 포함).

    Args:
        post_id: 글 ID
    """
    try:
        r = _wp_get(f"posts/{post_id}")
        if r.status_code != 200:
            return f"❌ 글 조회 실패: HTTP {r.status_code}"
        p = r.json()
        meta = p.get("meta", {})
        rm_meta = _get_rankmath_meta(post_id)
        lines = [
            f"## {p['title']['rendered']}",
            f"- ID: {p['id']}",
            f"- 상태: {p['status']}",
            f"- 날짜: {p.get('date', '')}",
            f"- URL: {p['link']}",
            f"- 슬러그: {p['slug']}",
            f"- 카테고리 ID: {p.get('categories', [])}",
            f"- 태그 ID: {p.get('tags', [])}",
            f"- 대표이미지 ID: {p.get('featured_media', 0)}",
        ]
        focus_kw = rm_meta.get("rank_math_focus_keyword", "") or meta.get("rank_math_focus_keyword", "")
        seo_t = rm_meta.get("rank_math_title", "") or meta.get("rank_math_title", "")
        meta_d = rm_meta.get("rank_math_description", "") or meta.get("rank_math_description", "")
        if focus_kw:
            lines.append(f"- 포커스 키워드: {focus_kw}")
        if seo_t:
            lines.append(f"- SEO 제목: {seo_t}")
        if meta_d:
            lines.append(f"- 메타 설명: {meta_d}")

        content = p["content"]["rendered"]
        if len(content) > 3000:
            content = content[:3000] + "\n... (잘림)"
        lines.append(f"\n### 본문\n{content}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ 글 조회 실패: {e}"


# ── 도구 8: 초안 목록 ────────────────────────────────────

@mcp.tool()
def wp_list_drafts() -> str:
    """리뷰 대기 중인 초안 + 예약 글 목록을 반환합니다."""
    all_posts = []
    for status in ("draft", "future"):
        try:
            r = _wp_get("posts", {"per_page": 50, "status": status, "orderby": "date", "order": "desc"})
            if r.status_code == 200:
                all_posts.extend(r.json())
        except Exception:
            pass

    if not all_posts:
        return "초안/예약 글이 없습니다."

    lines = [f"## 리뷰 대기 ({len(all_posts)}개)\n"]
    for p in sorted(all_posts, key=lambda x: x.get("date", ""), reverse=True):
        status_icon = "📝" if p["status"] == "draft" else "⏰"
        date_str = p.get("date", "")[:16].replace("T", " ")
        lines.append(f"{status_icon} [{p['status']}] **{p['title']['rendered']}**")
        lines.append(f"   ID: {p['id']} | {date_str} | {WP_URL}/?p={p['id']}&preview=true")
    return "\n".join(lines)


# ── SEO 수정 제안 생성 헬퍼 ─────────────────────────────

def _build_seo_suggestions(
    content: str,
    content_text: str,
    focus_keyword: str,
    seo_title: str,
    meta_description: str,
    slug: str,
    failed_checks: list[str],
) -> list[str]:
    """실패한 SEO 체크 항목에 대해 구체적 수정 제안을 생성한다."""
    kw = focus_keyword.lower()
    suggestions = []

    # ── 1. 첫 문단 키워드 ──
    if "keyword_in_intro" in failed_checks:
        first_p_match = re.search(r"<p\b[^>]*>(.*?)</p>", content, re.DOTALL | re.IGNORECASE)
        if first_p_match:
            first_p_text = re.sub(r"<[^>]+>", "", first_p_match.group(1)).strip()
            preview = first_p_text[:80] + ("..." if len(first_p_text) > 80 else "")
            suggestions.append(
                f"### 첫 문단에 키워드 삽입\n"
                f"현재 첫 문단: \"{preview}\"\n"
                f"→ 첫 1~2문장에 **'{focus_keyword}'**를 자연스럽게 포함시키세요.\n"
                f"예: \"{focus_keyword}(은/는) {first_p_text[:20]}...\""
            )
        else:
            suggestions.append(
                f"### 첫 문단에 키워드 삽입\n"
                f"본문 첫 10%에 **'{focus_keyword}'**를 포함시키세요."
            )

    # ── 2. 키워드 밀도 ──
    if "keyword_density" in failed_checks:
        content_text_lower = content_text.lower()
        kw_count = content_text_lower.count(kw)
        char_count = len(content_text)
        current_density = (kw_count * len(kw)) / char_count * 100 if char_count else 0
        min_count = max(1, int(char_count * 0.005 / max(len(kw), 1)))
        max_count = int(char_count * 0.025 / max(len(kw), 1))

        if current_density > 2.5:
            diff = kw_count - max_count
            kw_sentences = []
            for line in reversed(content.split("\n")):
                text = re.sub(r"<[^>]+>", "", line).strip()
                if kw in text.lower() and len(text) > 10:
                    is_heading = bool(re.search(r"<h[2-4]", line))
                    tag = "[H태그]" if is_heading else "[본문]"
                    kw_sentences.append(f"  {tag} \"{text[:70]}...\"")
                    if len(kw_sentences) >= min(diff + 2, 6):
                        break
            suggestions.append(
                f"### 키워드 밀도 조정 (과다)\n"
                f"현재: {current_density:.1f}% ({kw_count}회) → 목표: 0.5~2.5% ({min_count}~{max_count}회)\n"
                f"**{diff}회 이상 제거** 필요. 아래 문장에서 '{focus_keyword}'를 동의어로 교체:\n"
                + "\n".join(kw_sentences) + "\n"
                f"동의어 예시: '이 도구', '해당 기술', '이 방법', '해당 시스템'"
            )
        else:
            diff = min_count - kw_count
            no_kw_paragraphs = []
            for m in re.finditer(r"<p\b[^>]*>(.*?)</p>", content, re.DOTALL | re.IGNORECASE):
                p_text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
                if kw not in p_text.lower() and len(p_text) > 30:
                    no_kw_paragraphs.append(f"  \"{p_text[:70]}...\"")
                    if len(no_kw_paragraphs) >= min(diff + 2, 5):
                        break
            suggestions.append(
                f"### 키워드 밀도 조정 (부족)\n"
                f"현재: {current_density:.1f}% ({kw_count}회) → 목표: 0.5~2.5% ({min_count}~{max_count}회)\n"
                f"**{max(diff, 1)}회 이상 추가** 필요. 아래 문단에 '{focus_keyword}'를 자연스럽게 삽입:\n"
                + "\n".join(no_kw_paragraphs)
            )

    # ── 3. 소제목 키워드 ──
    if "keyword_in_headings" in failed_checks:
        h_all = re.findall(r"<(h[2-4])[^>]*>(.*?)</\1>", content, re.IGNORECASE)
        no_kw_headings = []
        for tag, text in h_all:
            clean = re.sub(r"<[^>]+>", "", text).strip()
            if kw not in clean.lower():
                no_kw_headings.append(f"  - <{tag}>{clean}</{tag}>")
        suggestions.append(
            f"### 소제목에 키워드 추가\n"
            f"키워드 없는 소제목 ({len(no_kw_headings)}개):\n"
            + "\n".join(no_kw_headings[:6]) + "\n"
            f"→ 최소 1개에 **'{focus_keyword}'**를 넣으세요."
        )

    # ── 4. 내부 링크 ──
    if "internal_links" in failed_checks:
        link_suggestions = []
        try:
            r = _wp_get("posts", {"per_page": 5, "search": focus_keyword, "status": "publish"})
            if r.status_code == 200:
                for p in r.json()[:3]:
                    t = p["title"]["rendered"]
                    u = p["link"]
                    link_suggestions.append(f"  - `<a href=\"{u}\">{t}</a>`")
        except Exception:
            pass
        msg = f"### 내부 링크 추가\n현재 내부 링크 0개. 최소 1개 필요.\n"
        if link_suggestions:
            msg += "관련 글 추천:\n" + "\n".join(link_suggestions)
        else:
            msg += f"`wp_find_internal_links('{focus_keyword}')` 도구를 사용하세요."
        suggestions.append(msg)

    # ── 5. 외부 링크 ──
    if "external_links" in failed_checks:
        suggestions.append(
            f"### 외부 링크 추가\n"
            f"본문에 관련 외부 링크 1개 이상 추가하세요.\n"
            f"예: 공식 문서, 위키피디아, 학술 논문, 권위 있는 블로그"
        )

    # ── 6. 메타 설명 길이 ──
    if "meta_desc_length" in failed_checks:
        md_len = len(meta_description) if meta_description else 0
        if md_len == 0:
            suggestions.append(
                f"### 메타 설명 설정\n"
                f"메타 설명이 없습니다. 120~160자로 작성하세요.\n"
                f"'{focus_keyword}'를 포함시키세요."
            )
        else:
            direction = "늘려" if md_len < 120 else "줄여"
            suggestions.append(
                f"### 메타 설명 길이 조정\n"
                f"현재: {md_len}자 → 목표: 120~160자 ({direction}주세요)\n"
                f"현재 내용: \"{meta_description}\""
            )

    # ── 7. SEO 제목 관련 ──
    if "seo_title_set" in failed_checks:
        suggestions.append(
            f"### SEO 제목 설정\n"
            f"SEO 제목이 설정되지 않았습니다. 30~60자로 작성하고 '{focus_keyword}'로 시작하세요."
        )
    else:
        title_issues = []
        if "title_length" in failed_checks:
            st_len = len(seo_title) if seo_title else 0
            title_issues.append(f"길이 {st_len}자 → 30~60자로 조정")
        if "title_starts_with_kw" in failed_checks:
            title_issues.append(f"'{focus_keyword}'로 시작하도록 변경")
        if "title_has_number" in failed_checks:
            title_issues.append("숫자 포함 (예: 7가지, 5단계, 2026)")
        if title_issues:
            suggestions.append(
                f"### SEO 제목 개선\n"
                f"현재: \"{seo_title}\"\n"
                + "\n".join(f"  - {t}" for t in title_issues)
            )

    return suggestions


# ── 도구 9: SEO 체크 ─────────────────────────────────────

@mcp.tool()
def wp_seo_check(content: str, focus_keyword: str, seo_title: str = "", meta_description: str = "", slug: str = "") -> str:
    """RankMath 기준에 맞춘 SEO 체크 + 구체적 수정 제안.

    체크리스트와 함께 실패 항목에 대한 구체적 수정 방법을 제시합니다.

    Args:
        content: HTML 본문
        focus_keyword: 포커스 키워드
        seo_title: SEO 제목
        meta_description: 메타 설명
        slug: URL 슬러그
    """
    kw = focus_keyword.lower()
    content_lower = content.lower()
    content_text = re.sub(r"<[^>]+>", " ", content).strip()
    content_text = re.sub(r"\s+", " ", content_text)
    content_text_lower = content_text.lower()
    char_count = len(content_text)
    word_count = len(content_text.split())

    checks = []
    score = 0
    total = 0
    failed_names = []

    def check(name: str, passed: bool, weight: int = 1, detail: str = "", check_name: str = ""):
        nonlocal score, total
        total += weight
        if passed:
            score += weight
        else:
            if check_name:
                failed_names.append(check_name)
        icon = "✅" if passed else "❌"
        msg = f"{icon} {name}"
        if detail:
            msg += f" — {detail}"
        checks.append(msg)

    # ── 기본 SEO (RankMath: Basic SEO) ────────────────────

    checks.append("\n**[기본 SEO]**")

    check("포커스 키워드가 SEO 제목에 포함", kw in (seo_title or "").lower(), 2,
          check_name="keyword_in_seo_title")

    if meta_description:
        check("포커스 키워드가 메타 설명에 포함", kw in meta_description.lower(), 2,
              check_name="keyword_in_meta_desc")
    else:
        check("메타 설명 설정", False, 2, "미설정", check_name="keyword_in_meta_desc")

    if slug:
        kw_parts = kw.split()
        slug_lower = slug.lower()
        check("포커스 키워드가 URL에 포함", any(p in slug_lower for p in kw_parts), 2,
              check_name="keyword_in_url")
    else:
        check("URL 슬러그 설정", False, 2, "미설정", check_name="keyword_in_url")

    first_10pct = content_text_lower[:max(len(content_text_lower) // 10, 200)]
    check("포커스 키워드가 본문 도입부에 포함", kw in first_10pct, 2,
          check_name="keyword_in_intro")

    check(f"본문 길이 ({char_count}자 / 약 {word_count}단어)", char_count >= 2500, 2,
          "RankMath 기준: 600단어+", check_name="content_length")

    check("포커스 키워드가 본문에 포함", kw in content_text_lower, 1,
          check_name="keyword_in_content")

    # ── 추가 SEO (RankMath: Additional) ───────────────────

    checks.append("\n**[추가 SEO]**")

    h_matches = re.findall(r"<h[2-4][^>]*>(.*?)</h[2-4]>", content, re.IGNORECASE)
    h_with_kw = sum(1 for h in h_matches if kw in h.lower())
    check(f"소제목(H2-H4)에 키워드 포함 ({h_with_kw}/{len(h_matches)}개)", h_with_kw >= 1, 2,
          check_name="keyword_in_headings")

    if content_text_lower:
        kw_count = content_text_lower.count(kw)
        density = (kw_count * len(kw)) / len(content_text_lower) * 100
        in_range = 0.5 <= density <= 2.5
        check(f"키워드 밀도 ({density:.1f}%, {kw_count}회)", in_range, 2,
              "RankMath 기준: 1~2.5%", check_name="keyword_density")

    img_tags = re.findall(r"<img[^>]*>", content, re.IGNORECASE)
    img_alts = re.findall(r'alt=["\']([^"\']*)["\']', content, re.IGNORECASE)
    has_images = len(img_tags) > 0
    alt_with_kw = sum(1 for alt in img_alts if kw in alt.lower())
    if has_images:
        check(f"이미지 alt에 키워드 ({alt_with_kw}/{len(img_tags)})", alt_with_kw >= 1, 1,
              check_name="img_alt_keyword")
    else:
        check("본문에 이미지 포함", False, 1, "이미지 없음 (대표이미지 별도)",
              check_name="has_images")

    if slug:
        slug_len = len(slug)
        check(f"URL 길이 ({slug_len}자)", slug_len <= 75, 1,
              "RankMath 기준: 75자 이하", check_name="url_length")

    internal_links = re.findall(rf'href=["\']({re.escape(WP_URL)}[^"\']*)["\']', content, re.IGNORECASE)
    check(f"내부 링크 ({len(internal_links)}개)", len(internal_links) >= 1, 2,
          "최소 1개", check_name="internal_links")

    all_links = re.findall(r'href=["\']([^"\']*)["\']', content, re.IGNORECASE)
    external_links = [l for l in all_links if l.startswith("http") and WP_URL not in l and not l.startswith("#")]
    check(f"외부 링크 ({len(external_links)}개)", len(external_links) >= 1, 1,
          "최소 1개 권장", check_name="external_links")

    # ── 제목 가독성 (RankMath: Title Readability) ─────────

    checks.append("\n**[제목 가독성]**")

    if seo_title:
        st_len = len(seo_title)
        check(f"SEO 제목 길이 ({st_len}자)", 30 <= st_len <= 60, 1,
              "RankMath 기준: 60자 이하", check_name="title_length")
    else:
        check("SEO 제목 설정", False, 1, "미설정", check_name="seo_title_set")

    if seo_title:
        check("제목이 키워드로 시작", (seo_title or "").lower().startswith(kw), 1,
              "SEO 가산점", check_name="title_starts_with_kw")

    if seo_title:
        has_number = bool(re.search(r"\d", seo_title))
        check("제목에 숫자 포함", has_number, 1, "CTR 향상",
              check_name="title_has_number")

    # ── 콘텐츠 가독성 (RankMath: Content Readability) ─────

    checks.append("\n**[콘텐츠 가독성]**")

    if meta_description:
        md_len = len(meta_description)
        check(f"메타 설명 길이 ({md_len}자)", 120 <= md_len <= 160, 1,
              "RankMath 기준: 120~160자", check_name="meta_desc_length")

    paragraphs = re.findall(r"<p\b[^>]*>(.*?)</p>", content, re.DOTALL | re.IGNORECASE)
    long_paragraphs = [p for p in paragraphs if len(re.sub(r"<[^>]+>", "", p).strip()) > 300]
    check(f"짧은 단락 ({len(long_paragraphs)}개 > 300자)", len(long_paragraphs) == 0, 1,
          "긴 단락 분리 권장", check_name="short_paragraphs")

    has_media = bool(img_tags) or "<video" in content_lower or "<iframe" in content_lower
    check("미디어(이미지/비디오) 포함", has_media, 1, check_name="has_media")

    # ── 추가 품질 체크 ────────────────────────────────────

    checks.append("\n**[추가 품질]**")

    has_faq_schema = "application/ld+json" in content_lower and "faqpage" in content_lower
    check("FAQ JSON-LD 스키마", has_faq_schema, 1, check_name="faq_schema")

    h2_matches = re.findall(r"<h2[^>]*>(.*?)</h2>", content, re.IGNORECASE)
    check(f"H2 소제목 구조 ({len(h2_matches)}개)", 3 <= len(h2_matches) <= 8, 1,
          "3~8개 권장", check_name="h2_structure")

    # ── 점수 계산 ─────────────────────────────────────────
    pct = int((score / total) * 100) if total > 0 else 0

    if pct >= 80:
        grade = "🟢 Good"
    elif pct >= 60:
        grade = "🟡 개선 권장"
    else:
        grade = "🔴 수정 필수"

    result = f"## MCP SEO 체크: {pct}/100 {grade}"
    result += f"\n⚠️ RankMath 실제 점수는 WP 에디터에서 확인하세요.\n"
    result += "\n".join(checks)

    # ── 수정 제안 섹션 ────────────────────────────────────
    if failed_names:
        seo_suggestions = _build_seo_suggestions(
            content=content,
            content_text=content_text,
            focus_keyword=focus_keyword,
            seo_title=seo_title,
            meta_description=meta_description,
            slug=slug,
            failed_checks=failed_names,
        )
        if seo_suggestions:
            result += f"\n\n---\n## 수정 제안 ({len(seo_suggestions)}개)\n\n"
            result += "\n\n".join(seo_suggestions)

    return result


# ── 도구 10: 이미지 검색 + 업로드 ────────────────────────

@mcp.tool()
def wp_find_image(keyword: str, upload: bool = True, focus_keyword: str = "") -> str:
    """키워드로 무료 스톡 이미지를 검색하고 WordPress에 업로드합니다.

    Args:
        keyword: 검색 키워드 (한/영 모두 가능, 영문 추천)
        upload: True면 WordPress에 업로드, False면 URL만 반환
        focus_keyword: 포커스 키워드 (alt 태그에 사용, 비면 keyword 사용)
    """
    image_url = None
    source = ""
    photographer = ""

    # 1. Unsplash
    if UNSPLASH_ACCESS_KEY:
        try:
            r = httpx.get(
                "https://api.unsplash.com/search/photos",
                params={"query": keyword, "orientation": "landscape", "per_page": 3},
                headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
                timeout=15,
            )
            if r.status_code == 200:
                results = r.json().get("results", [])
                if results:
                    photo = results[0]
                    image_url = photo["urls"]["regular"]
                    source = "Unsplash"
                    photographer = photo.get("user", {}).get("name", "Unknown")
        except Exception:
            pass

    # 2. Pexels fallback
    if not image_url and PEXELS_API_KEY:
        try:
            r = httpx.get(
                "https://api.pexels.com/v1/search",
                params={"query": keyword, "orientation": "landscape", "per_page": 3},
                headers={"Authorization": PEXELS_API_KEY},
                timeout=15,
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    image_url = photos[0]["src"]["large"]
                    source = "Pexels"
                    photographer = photos[0].get("photographer", "Unknown")
        except Exception:
            pass

    # 3. Pixabay fallback
    if not image_url and PIXABAY_API_KEY:
        try:
            r = httpx.get(
                "https://pixabay.com/api/",
                params={"key": PIXABAY_API_KEY, "q": keyword, "image_type": "photo",
                        "orientation": "horizontal", "per_page": 3},
                timeout=15,
            )
            if r.status_code == 200:
                hits = r.json().get("hits", [])
                if hits:
                    image_url = hits[0]["largeImageURL"]
                    source = "Pixabay"
                    photographer = hits[0].get("user", "Unknown")
        except Exception:
            pass

    # 4. WordPress 미디어 라이브러리 fallback
    if not image_url:
        try:
            r = _wp_get("media", {"per_page": 5, "search": keyword, "media_type": "image"})
            if r.status_code == 200:
                images = r.json()
                if images:
                    media = images[0]
                    media_id = media["id"]
                    media_url = media.get("source_url", "")
                    media_title = media.get("title", {}).get("rendered", "")
                    if upload:
                        return "\n".join([
                            f"🖼️ 미디어 라이브러리에서 기존 이미지 발견",
                            f"- 미디어 ID: {media_id}",
                            f"- URL: {media_url}",
                            f"- 제목: {media_title}",
                            f"",
                            f"wp_create_post()에서 featured_media_id={media_id} 로 사용하세요.",
                        ])
                    else:
                        return f"🖼️ 미디어 라이브러리에서 발견\n- ID: {media_id}\n- URL: {media_url}"
        except Exception:
            pass

    if not image_url:
        missing = []
        if not UNSPLASH_ACCESS_KEY:
            missing.append("UNSPLASH_ACCESS_KEY")
        if not PEXELS_API_KEY:
            missing.append("PEXELS_API_KEY")
        if not PIXABAY_API_KEY:
            missing.append("PIXABAY_API_KEY")
        if missing:
            return (
                f"❌ 이미지 API 키 미설정: {', '.join(missing)}\n"
                f".env 파일에 추가하세요.\n\n"
                f"무료 API 키 발급:\n"
                f"- Pexels: https://www.pexels.com/api/ (추천, 무료)\n"
                f"- Pixabay: https://pixabay.com/api/docs/ (무료)\n"
                f"- Unsplash: https://unsplash.com/developers (무료)"
            )
        return f"❌ '{keyword}'에 대한 이미지를 찾을 수 없습니다."

    if not upload:
        return f"🖼️ 이미지 발견\n- URL: {image_url}\n- 출처: {source}\n- 작가: {photographer}"

    # WordPress에 업로드
    try:
        img_r = httpx.get(image_url, timeout=30, follow_redirects=True)
        if img_r.status_code != 200:
            return f"❌ 이미지 다운로드 실패: HTTP {img_r.status_code}"

        content_type = img_r.headers.get("content-type", "image/jpeg")
        ext = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]
        filename = f"{keyword.replace(' ', '-')[:30]}.{ext}"

        upload_r = httpx.post(
            f"{API_BASE}/media",
            headers={
                **_auth_header(),
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": content_type,
            },
            content=img_r.content,
            timeout=60,
            follow_redirects=True,
        )

        if upload_r.status_code in (200, 201):
            media = upload_r.json()
            # alt 텍스트 설정 (포커스 키워드 우선)
            alt_kw = focus_keyword or keyword
            alt_text = f"{alt_kw} - {source} ({photographer})"
            _wp_post(f"media/{media['id']}", {"alt_text": alt_text})

            return "\n".join([
                f"✅ 이미지 업로드 완료",
                f"- 미디어 ID: {media['id']}",
                f"- URL: {media.get('source_url', '')}",
                f"- alt: {alt_text}",
                f"- 출처: {source} / {photographer}",
                f"",
                f"wp_create_post()에서 featured_media_id={media['id']} 로 사용하세요.",
            ])
        else:
            return f"❌ 업로드 실패: HTTP {upload_r.status_code}\n{upload_r.text[:300]}"
    except Exception as e:
        return f"❌ 이미지 업로드 실패: {e}"


# ── 도구 11: 미디어 직접 업로드 ──────────────────────────

@mcp.tool()
def wp_upload_media(image_url: str, alt_text: str = "") -> str:
    """URL에서 이미지를 다운로드하여 WordPress 미디어 라이브러리에 업로드합니다.

    Args:
        image_url: 이미지 URL
        alt_text: alt 태그 텍스트
    """
    try:
        img_r = httpx.get(image_url, timeout=30, follow_redirects=True)
        if img_r.status_code != 200:
            return f"❌ 이미지 다운로드 실패: HTTP {img_r.status_code}"

        content_type = img_r.headers.get("content-type", "image/jpeg")
        ext = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]
        filename = f"upload-{int(time.time())}.{ext}"

        upload_r = httpx.post(
            f"{API_BASE}/media",
            headers={
                **_auth_header(),
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": content_type,
            },
            content=img_r.content,
            timeout=60,
            follow_redirects=True,
        )

        if upload_r.status_code in (200, 201):
            media = upload_r.json()
            if alt_text:
                _wp_post(f"media/{media['id']}", {"alt_text": alt_text})
            return f"✅ 업로드 완료\n- 미디어 ID: {media['id']}\n- URL: {media.get('source_url', '')}"
        else:
            return f"❌ 업로드 실패: HTTP {upload_r.status_code}\n{upload_r.text[:300]}"
    except Exception as e:
        return f"❌ 업로드 실패: {e}"


# ── 내부 링크 매칭용 캐시 + 헬퍼 ─────────────────────────
_posts_keywords_cache: list[dict] | None = None
_posts_keywords_ts: float = 0


def _get_posts_keywords() -> list[dict]:
    """발행 글의 ID/제목/URL/포커스키워드/카테고리를 가져온다 (1시간 캐시)."""
    global _posts_keywords_cache, _posts_keywords_ts
    if _posts_keywords_cache is not None and (time.time() - _posts_keywords_ts) < 3600:
        return _posts_keywords_cache
    try:
        r = httpx.get(
            f"{WP_URL}/wp-json/custom/v1/posts-keywords",
            headers=_auth_header(), timeout=TIMEOUT, follow_redirects=True,
        )
        if r.status_code == 200:
            _posts_keywords_cache = r.json()
            _posts_keywords_ts = time.time()
            return _posts_keywords_cache
    except Exception:
        pass
    return []


def _keyword_similarity(kw_a: str, kw_b: str) -> float:
    """두 키워드의 단어 Jaccard 유사도 (0.0~1.0)."""
    if not kw_a or not kw_b:
        return 0.0
    words_a = set(kw_a.lower().split())
    words_b = set(kw_b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


# ── 도구 12: 내부 링크 추천 (3단계 매칭) ─────────────────

@mcp.tool()
def wp_find_internal_links(focus_keyword: str, post_id: int = 0) -> str:
    """기존 글 중 관련 글을 찾아서 내부 링크 후보를 추천합니다.

    3단계 매칭: 포커스 키워드 유사도 → WP 검색 API → 카테고리 보너스.

    Args:
        focus_keyword: 현재 글의 포커스 키워드
        post_id: 현재 글 ID (자기 자신 제외용, 0이면 제외 없음)
    """
    scored: dict[int, dict] = {}

    # ── 1단계: 포커스 키워드 매칭 (posts-keywords 엔드포인트) ──
    all_posts = _get_posts_keywords()
    for p in all_posts:
        pid = p["id"]
        if pid == post_id:
            continue
        fk = p.get("focus_keyword", "")
        sim = _keyword_similarity(focus_keyword, fk)
        if sim <= 0:
            continue
        pts = 10.0 if focus_keyword.lower() == fk.lower() else sim * 7.0
        scored[pid] = {
            "score": pts,
            "title": p["title"],
            "url": p["url"],
            "categories": p.get("categories", []),
            "reasons": [f"키워드유사도 {sim:.0%}"],
        }

    # ── 2단계: WP 검색 API — 제목+excerpt 매칭 ──
    kw_words = set(focus_keyword.lower().split())
    try:
        r = _wp_get("posts", {"per_page": 50, "search": focus_keyword, "status": "publish"})
        if r.status_code == 200:
            for p in r.json():
                pid = p["id"]
                if pid == post_id:
                    continue
                title = p["title"]["rendered"]
                title_lower = title.lower()
                excerpt_lower = re.sub(r"<[^>]+>", "", p.get("excerpt", {}).get("rendered", "")).lower()

                title_hits = sum(1 for w in kw_words if w in title_lower)
                excerpt_hits = sum(1 for w in kw_words if w in excerpt_lower)
                title_pts = min(title_hits / max(len(kw_words), 1) * 5.0, 5.0)
                excerpt_pts = min(excerpt_hits / max(len(kw_words), 1) * 3.0, 3.0)
                pts = title_pts + excerpt_pts

                if pts <= 0:
                    continue

                if pid in scored:
                    scored[pid]["score"] += pts
                    scored[pid]["reasons"].append(f"검색매칭 +{pts:.1f}")
                else:
                    scored[pid] = {
                        "score": pts,
                        "title": title,
                        "url": p["link"],
                        "categories": p.get("categories", []),
                        "reasons": [f"검색매칭 {pts:.1f}"],
                    }
    except Exception:
        pass

    # ── 3단계: 카테고리 보너스 ──
    my_cats: set[int] = set()
    if post_id:
        try:
            r = _wp_get(f"posts/{post_id}", {"_fields": "categories"})
            if r.status_code == 200:
                my_cats = set(r.json().get("categories", []))
        except Exception:
            pass
    else:
        for p in all_posts:
            fk = p.get("focus_keyword", "")
            if _keyword_similarity(focus_keyword, fk) > 0.5:
                my_cats.update(p.get("categories", []))
                break

    if my_cats:
        for data in scored.values():
            post_cats = set(data.get("categories", []))
            if post_cats & my_cats:
                data["score"] += 3.0
                data["reasons"].append("같은카테고리 +3")

    # ── 결과 정렬 + 상위 7개 ──
    ranked = sorted(scored.values(), key=lambda x: x["score"], reverse=True)[:7]

    if not ranked:
        return f"'{focus_keyword}' 관련 기존 글을 찾을 수 없습니다."

    lines = [f"## 내부 링크 추천 ({len(ranked)}개)\n"]
    for i, s in enumerate(ranked, 1):
        title = s["title"]
        url = s["url"]
        score_val = s["score"]
        reasons = ", ".join(s["reasons"])
        anchor = title if len(title) <= 25 else title[:22] + "..."
        grade = "🔴" if score_val >= 8 else "🟡" if score_val >= 4 else "⚪"

        lines.append(f"### {i}. {grade} {title} (점수: {score_val:.1f})")
        lines.append(f"  매칭: {reasons}")
        lines.append(f"  HTML: `<a href=\"{url}\">{anchor}</a>`")
        lines.append("")

    lines.append("---")
    lines.append("💡 **양방향 링크 팁**: 위 글에서도 현재 글로 링크를 추가하면 SEO 효과가 올라갑니다.")
    lines.append("  `wp_get_post(id)` → 본문에 현재 글 링크 삽입 → `wp_update_post(id, content=...)`")

    return "\n".join(lines)


# ── 도구 13: 초안 리뷰 ───────────────────────────────────

@mcp.tool()
def wp_review_draft(post_id: int) -> str:
    """초안 글의 SEO 점수, 체크리스트, 미리보기 링크를 종합 리포트합니다.

    Args:
        post_id: 리뷰할 글 ID
    """
    try:
        r = _wp_get(f"posts/{post_id}")
        if r.status_code != 200:
            return f"❌ 글 조회 실패: HTTP {r.status_code}"
        post = r.json()
    except Exception as e:
        return f"❌ 글 조회 실패: {e}"

    title = post["title"]["rendered"]
    content = post["content"]["rendered"]
    status = post["status"]
    # WP REST API meta + RankMath 로컬 캐시 병합
    meta = post.get("meta", {})
    rm_meta = _get_rankmath_meta(post_id)
    focus_kw = rm_meta.get("rank_math_focus_keyword", "") or meta.get("rank_math_focus_keyword", "")
    seo_title = rm_meta.get("rank_math_title", "") or meta.get("rank_math_title", "")
    meta_desc = rm_meta.get("rank_math_description", "") or meta.get("rank_math_description", "")
    slug = post.get("slug", "")
    excerpt = post.get("excerpt", {}).get("rendered", "")
    featured = post.get("featured_media", 0)

    content_text = re.sub(r"<[^>]+>", " ", content).strip()

    # 서버사이드 SEO 점수 계산 (자동)
    seo_data = _compute_seo_score(post_id)

    lines = [
        f"## 리뷰: {title}",
        f"- ID: {post['id']}",
        f"- 상태: {status}",
        f"- 미리보기: {WP_URL}/?p={post['id']}&preview=true",
        f"- 슬러그: /{slug}/",
        f"- 분량: {len(content_text)}자",
        f"- 대표이미지: {'✅ 설정됨 (ID: ' + str(featured) + ')' if featured else '❌ 미설정'}",
        f"- 카테고리 ID: {post.get('categories', [])}",
        f"- 태그 ID: {post.get('tags', [])}",
        "",
    ]

    # SEO 점수 (서버사이드 계산)
    if seo_data and 'score' in seo_data:
        seo_score = seo_data['score']
        if seo_score >= 80:
            seo_grade = "🟢 Good"
        elif seo_score >= 50:
            seo_grade = "🟡 개선 권장"
        else:
            seo_grade = "🔴 수정 필수"
        lines.append(f"### SEO 점수: {seo_score}/100 {seo_grade}")

        # 실패한 항목 표시
        failed = [c for c in seo_data.get('checks', []) if not c['passed']]
        if failed:
            lines.append("**실패 항목:**")
            check_labels = {
                'keyword_in_seo_title': '키워드 → SEO 제목',
                'keyword_in_meta_desc': '키워드 → 메타설명',
                'keyword_in_url': '키워드 → URL',
                'keyword_in_intro': '키워드 → 도입부',
                'content_length': '본문 길이 2500자+',
                'keyword_in_content': '키워드 → 본문',
                'keyword_in_headings': '키워드 → 소제목(H2-H4)',
                'keyword_density': '키워드 밀도 1~2.5%',
                'has_images': '본문 이미지',
                'url_length': 'URL 75자 이하',
                'internal_links': '내부 링크 1개+',
                'external_links': '외부 링크 1개+',
                'title_length': 'SEO 제목 60자 이하',
                'title_starts_with_kw': '제목이 키워드로 시작',
                'title_has_number': '제목에 숫자',
                'seo_title_set': 'SEO 제목 설정',
                'meta_desc_length': '메타설명 120~160자',
                'short_paragraphs': '단락 300자 이하',
                'faq_schema': 'FAQ 스키마',
                'h2_structure': 'H2 3~8개',
            }
            for c in failed:
                label = check_labels.get(c['name'], c['name'])
                lines.append(f"  ❌ {label} (가중치: {c['weight']})")
    else:
        lines.append("### SEO 점수: 계산 실패")

    lines.extend([
        "",
        "### SEO 필드",
        f"- 포커스 키워드: {focus_kw or '❌ 미설정'}",
        f"- SEO 제목: {seo_title or '❌ 미설정'}",
        f"- 메타 설명: {meta_desc or '❌ 미설정'}",
        f"- Excerpt: {excerpt[:100] or '❌ 미설정'}",
        "",
    ])

    # MCP 자체 SEO 체크
    if focus_kw:
        seo_result = wp_seo_check(content, focus_kw, seo_title, meta_desc, slug)
        lines.append(seo_result)
    else:
        lines.append("⚠️ 포커스 키워드가 설정되지 않아 SEO 체크를 생략합니다.")

    lines.extend([
        "",
        "### 다음 단계",
        f'- 수정: wp_update_post(post_id={post["id"]}, ...)',
        f'- 예약 발행: wp_schedule_draft(post_id={post["id"]}, publish_date="2026-02-20T09:00:00")',
        f'- 즉시 발행: wp_update_post(post_id={post["id"]}, status="publish")',
    ])

    return "\n".join(lines)


# ── 도구 14: 초안 예약 발행 ──────────────────────────────

@mcp.tool()
def wp_schedule_draft(post_id: int, publish_date: str) -> str:
    """초안을 예약 발행으로 전환합니다.

    Args:
        post_id: 글 ID
        publish_date: 발행 시간 (ISO 8601, 예: "2026-02-20T09:00:00")
    """
    try:
        r = _wp_post(f"posts/{post_id}", {
            "status": "future",
            "date": publish_date,
        })
        if r.status_code in (200, 201):
            post = r.json()
            return f"✅ 예약 발행 설정 완료\n- ID: {post['id']}\n- 발행 예정: {post.get('date', publish_date)}\n- URL: {post['link']}"
        else:
            return f"❌ 예약 설정 실패: HTTP {r.status_code}\n{r.text[:500]}"
    except Exception as e:
        return f"❌ 예약 설정 실패: {e}"


# ── 도구 15: 통합 파이프라인 ──────────────────────────────

@mcp.tool()
def wp_publish_pipeline(
    title: str,
    content: str,
    focus_keyword: str,
    seo_title: str = "",
    meta_description: str = "",
    slug: str = "",
    excerpt: str = "",
    category: str = "",
    tags: str = "",
    image_keyword: str = "",
) -> str:
    """글 작성 → 이미지 업로드 → SEO 설정 → 리뷰까지 한번에 처리합니다.
    리뷰 결과를 반환하며, 예약/발행은 사용자에게 확인 후 진행하세요.

    Args:
        title: 글 제목
        content: HTML 본문
        focus_keyword: 포커스 키워드
        seo_title: SEO 제목 (비면 title 사용)
        meta_description: 메타 설명
        slug: URL 슬러그 (비면 focus_keyword로 자동 생성)
        excerpt: 요약문
        category: 카테고리 이름 (예: "테크", "AI")
        tags: 쉼표로 구분된 태그
        image_keyword: 이미지 검색 키워드 (영문 추천, 비면 focus_keyword 사용)
    """
    lines = ["## 📝 글 발행 파이프라인\n"]

    # ── Step 1: 이미지 검색 + 업로드 + 본문 자동 삽입 ──
    img_kw = image_keyword or focus_keyword
    featured_media_id = 0
    img_url = ""
    img_result = wp_find_image(img_kw, upload=True, focus_keyword=focus_keyword)
    if "미디어 ID:" in img_result:
        id_match = re.search(r"미디어 ID: (\d+)", img_result)
        url_match = re.search(r"URL: (https?://\S+)", img_result)
        if id_match:
            featured_media_id = int(id_match.group(1))
            img_url = url_match.group(1) if url_match else ""
            lines.append(f"✅ **Step 1** 이미지 업로드 (ID: {featured_media_id})")
        else:
            lines.append(f"⚠️ **Step 1** 이미지 업로드 — ID 추출 실패")
    else:
        lines.append(f"⚠️ **Step 1** 이미지 — {img_result.split(chr(10))[0]}")

    # 본문에 이미지가 없으면 첫 문단 뒤에 자동 삽입
    if img_url and "<img" not in content.lower():
        img_tag = f'\n<img src="{img_url}" alt="{focus_keyword}" width="800" />\n'
        # 첫 번째 </p> 뒤에 삽입
        first_p_end = content.find("</p>")
        if first_p_end != -1:
            content = content[:first_p_end + 4] + img_tag + content[first_p_end + 4:]
        else:
            content = img_tag + content
        lines.append(f"✅ **Step 1b** 본문에 이미지 자동 삽입")

    # ── Step 2: 글 생성 ──
    create_result = wp_create_post(
        title=title,
        content=content,
        focus_keyword=focus_keyword,
        seo_title=seo_title or title,
        meta_description=meta_description,
        slug=slug,
        excerpt=excerpt,
        category=category,
        tags=tags,
        featured_media_id=featured_media_id,
        status="draft",
    )

    if "❌" in create_result:
        lines.append(f"❌ **Step 2** 글 생성 실패")
        lines.append(create_result)
        return "\n".join(lines)

    # ID 추출
    id_match = re.search(r"ID: (\d+)", create_result)
    if not id_match:
        lines.append(f"❌ **Step 2** 글 생성 — ID 추출 실패")
        return "\n".join(lines)

    post_id = int(id_match.group(1))
    lines.append(f"✅ **Step 2** 글 생성 (ID: {post_id})")

    # ── Step 3: 리뷰 ──
    review_result = wp_review_draft(post_id)
    lines.append(f"✅ **Step 3** 리뷰 완료\n")
    lines.append(review_result)

    # ── 다음 단계 안내 ──
    lines.append(f"\n---")
    lines.append(f"### 🗓️ 다음 단계")
    lines.append(f"사용자에게 예약 발행 날짜를 물어보세요.")
    lines.append(f"- 예약: `wp_schedule_draft(post_id={post_id}, publish_date='날짜')`")
    lines.append(f"- 즉시 발행: `wp_update_post(post_id={post_id}, status='publish')`")
    lines.append(f"- 미리보기: {WP_URL}/?p={post_id}&preview=true")

    return "\n".join(lines)


# ── 도구 16: SEO 자동 최적화 ─────────────────────────────

@mcp.tool()
def wp_seo_optimize(post_id: int) -> str:
    """기존 글의 SEO 점수를 분석하고 자동 수정 가능한 항목을 즉시 적용합니다.

    자동 수정:
    - 슬러그에 포커스 키워드 삽입 (keyword_in_url)
    - 이미지 없으면 Pexels 검색→업로드→본문 삽입 (has_images)
    - 300자 이상 문단 자동 분리 (short_paragraphs)
    - H2 9개 이상이면 뒤쪽 H2를 H3으로 변환 (h2_structure)

    분석 후 Claude에게 지시:
    - 키워드 밀도 조정 (어떤 문장의 키워드를 교체할지 구체 지시)
    - 메타 설명 길이 조정 (현재 길이와 목표 범위)
    - 외부 링크 추가 (필요 시)
    - 소제목에 키워드 추가 (필요 시)

    Args:
        post_id: 최적화할 글 ID
    """
    lines = [f"## SEO 최적화 리포트 (Post {post_id})\n"]

    # ── 1단계: 현재 상태 수집 ──
    try:
        r = httpx.get(
            f"{API_BASE}/posts/{post_id}",
            params={"context": "edit"},
            headers=_auth_header(), timeout=TIMEOUT, follow_redirects=True,
        )
        if r.status_code != 200:
            return f"❌ 글 조회 실패: HTTP {r.status_code}"
        post = r.json()
    except Exception as e:
        return f"❌ 글 조회 실패: {e}"

    content = post["content"]["raw"]
    title = post["title"]["raw"]
    slug = post["slug"]
    meta = post.get("meta", {})
    focus_kw = meta.get("rank_math_focus_keyword", "")
    seo_title = meta.get("rank_math_title", "")
    meta_desc = meta.get("rank_math_description", "")
    featured = post.get("featured_media", 0)

    if not focus_kw:
        return "❌ 포커스 키워드가 설정되지 않았습니다. wp_update_post로 먼저 설정하세요."

    # SEO 점수 가져오기
    seo_data = _compute_seo_score(post_id)
    if not seo_data:
        return "❌ SEO 점수 계산 실패. 서버사이드 SEO endpoint를 확인하세요."

    before_score = seo_data["score"]
    failed = {c["name"]: c for c in seo_data.get("checks", []) if not c["passed"]}
    passed = {c["name"]: c for c in seo_data.get("checks", []) if c["passed"]}
    density = seo_data.get("density", 0)

    lines.append(f"### 수정 전: {before_score}/100 (실패 {len(failed)}개)\n")

    if not failed:
        lines.append("✅ 모든 SEO 항목 통과! 수정할 것이 없습니다.")
        return "\n".join(lines)

    auto_fixed = []
    manual_needed = []
    content_changed = False
    meta_updates = {}  # WP REST API meta로 업데이트할 필드
    post_updates = {}  # WP REST API post로 업데이트할 필드

    # ── 2단계: 자동 수정 ──

    # (A) keyword_in_url — 슬러그에 키워드 삽입
    if "keyword_in_url" in failed:
        new_slug = _keyword_to_slug(focus_kw)
        post_updates["slug"] = new_slug
        auto_fixed.append(f"슬러그 변경: `{slug}` → `{new_slug}`")

    # (B) has_images — 이미지 검색→업로드→본문 삽입
    if "has_images" in failed:
        img_result = wp_find_image(focus_kw, upload=True, focus_keyword=focus_kw)
        if "미디어 ID:" in img_result:
            id_match = re.search(r"미디어 ID: (\d+)", img_result)
            url_match = re.search(r"URL: (https?://\S+)", img_result)
            if id_match and url_match:
                media_id = int(id_match.group(1))
                img_url = url_match.group(1)
                post_updates["featured_media"] = media_id
                # 본문에 이미지 삽입
                if "<img" not in content.lower():
                    img_tag = f'\n<img src="{img_url}" alt="{focus_kw}" width="800" />\n'
                    first_p = content.find("</p>")
                    if first_p != -1:
                        content = content[:first_p + 4] + img_tag + content[first_p + 4:]
                    else:
                        content = img_tag + content
                    content_changed = True
                auto_fixed.append(f"이미지 업로드 + 본문 삽입 (ID: {media_id})")
        else:
            manual_needed.append(("이미지 추가", "wp_find_image로 이미지를 검색하고 본문에 삽입하세요."))

    # (C) short_paragraphs — 300자 이상 문단 자동 분리
    if "short_paragraphs" in failed:
        p_pattern = re.compile(r'(<p\b[^>]*>)(.*?)(</p>)', re.DOTALL | re.IGNORECASE)
        split_count = 0

        def _split_long_p(m):
            nonlocal split_count
            open_tag, inner, close_tag = m.group(1), m.group(2), m.group(3)
            text = re.sub(r'<[^>]+>', '', inner)
            if len(text) <= 300:
                return m.group(0)
            # 문장 단위로 분리 (. 다음 공백)
            sentences = re.split(r'(?<=[.!?다요죠함됩])\s+', inner)
            if len(sentences) < 2:
                return m.group(0)
            # 절반 지점에서 분리
            mid = len(sentences) // 2
            part1 = ' '.join(sentences[:mid])
            part2 = ' '.join(sentences[mid:])
            split_count += 1
            return f'{open_tag}{part1}{close_tag}\n\n{open_tag}{part2}{close_tag}'

        new_content = p_pattern.sub(_split_long_p, content)
        if split_count > 0:
            content = new_content
            content_changed = True
            auto_fixed.append(f"긴 문단 {split_count}개 자동 분리 (300자 기준)")

    # (D) h2_structure — H2가 9개 이상이면 뒤쪽을 H3으로 변환
    if "h2_structure" in failed:
        h2_matches = list(re.finditer(r'<h2([^>]*)>(.*?)</h2>', content, re.IGNORECASE))
        h2_count = len(h2_matches)
        if h2_count > 8:
            # 뒤에서부터 H3으로 변환 (FAQ 제외, 기법 번호가 있는 것 우선)
            converted = 0
            for m in reversed(h2_matches):
                if h2_count - converted <= 8:
                    break
                h2_text = m.group(2)
                # FAQ, 자주 묻는 질문은 유지
                if '자주 묻는' in h2_text or 'FAQ' in h2_text.upper():
                    continue
                # 포커스 키워드가 포함된 H2는 유지 (최소 1개)
                if focus_kw.lower() in h2_text.lower() and converted == 0:
                    continue
                old = m.group(0)
                new = f'<h3{m.group(1)}>{h2_text}</h3>'
                content = content.replace(old, new, 1)
                converted += 1
            if converted > 0:
                content_changed = True
                auto_fixed.append(f"H2 {converted}개 → H3으로 변환 ({h2_count}개 → {h2_count - converted}개)")
        elif h2_count < 3:
            manual_needed.append(("H2 소제목 추가", f"현재 H2가 {h2_count}개입니다. 3개 이상으로 늘려주세요."))

    # ── 3단계: 자동 수정 적용 ──

    if content_changed:
        post_updates["content"] = content

    if post_updates:
        try:
            httpx.post(
                f"{API_BASE}/posts/{post_id}",
                headers={**_auth_header(), "Content-Type": "application/json"},
                json=post_updates, timeout=TIMEOUT, follow_redirects=True,
            )
        except Exception as e:
            lines.append(f"⚠️ 자동 수정 적용 실패: {e}")

    if meta_updates:
        try:
            httpx.post(
                f"{API_BASE}/posts/{post_id}",
                headers={**_auth_header(), "Content-Type": "application/json"},
                json={"meta": meta_updates}, timeout=TIMEOUT, follow_redirects=True,
            )
        except Exception as e:
            lines.append(f"⚠️ 메타 업데이트 실패: {e}")

    # ── 4단계: 수동 수정 지시 생성 ──

    # (E) keyword_density — 키워드 밀도 분석 + 교체 지시
    if "keyword_density" in failed:
        content_text = re.sub(r'<[^>]+>', '', content)
        kw_lower = focus_kw.lower()
        kw_count = content_text.lower().count(kw_lower)
        char_count = len(content_text)
        current_density = (kw_count * len(kw_lower)) / char_count * 100 if char_count else 0

        # 목표: 밀도 1.5~2.0%
        target_count = int(char_count * 0.018 / len(kw_lower))  # 1.8% 타겟
        remove_count = max(0, kw_count - target_count)

        # 키워드가 포함된 문장 목록 (교체 후보)
        sentences_with_kw = []
        for line in content.split('\n'):
            text = re.sub(r'<[^>]+>', '', line).strip()
            if kw_lower in text.lower() and len(text) > 10:
                # H2 태그 안의 키워드는 별도 표시
                is_heading = bool(re.search(r'<h[2-4]', line))
                sentences_with_kw.append((text[:80], is_heading))

        instruction = (
            f"키워드 밀도 조정 필요: 현재 {current_density:.1f}% ({kw_count}회) → 목표 0.5~2.5%\n"
            f"  **{remove_count}회 제거** 필요. 아래 문장에서 '{focus_kw}'를 동의어로 교체:\n"
            f"  동의어 예시: '이 도구', '이 기술', '이 시스템', '해당 방법' 등\n"
        )
        for text, is_h in sentences_with_kw:
            tag = "[H2]" if is_h else "[본문]"
            instruction += f"  {tag} {text}...\n"

        manual_needed.append(("키워드 밀도 조정", instruction))

    # (F) meta_desc_length — 메타 설명 길이
    if "meta_desc_length" in failed:
        md_len = len(meta_desc) if meta_desc else 0
        direction = "늘려" if md_len < 120 else "줄여"
        manual_needed.append((
            "메타 설명 길이 조정",
            f"현재 {md_len}자 → 120~160자로 {direction}주세요.\n"
            f"  현재: {meta_desc}\n"
            f"  wp_update_post(post_id={post_id}, meta_description='새 설명') 으로 업데이트\n"
            f"  ⚠️ 또는 WP REST API meta 필드로 직접 업데이트 (더 확실)"
        ))

    # (G) external_links
    if "external_links" in failed:
        manual_needed.append((
            "외부 링크 추가",
            f"본문에 관련 외부 링크 1개 이상 추가하세요.\n"
            f"  예: 공식 문서, 위키피디아, 논문 등\n"
            f"  wp_update_post(post_id={post_id}, content='수정된 HTML') 으로 업데이트"
        ))

    # (H) keyword_in_headings
    if "keyword_in_headings" in failed:
        manual_needed.append((
            "소제목에 키워드 추가",
            f"H2~H4 소제목 중 최소 1개에 '{focus_kw}' 포함시켜주세요.\n"
            f"  예: '<h2>{focus_kw} — 핵심 개념</h2>'"
        ))

    # (I) 기타 실패 항목
    other_checks = {
        "keyword_in_seo_title": f"SEO 제목에 '{focus_kw}' 포함시키세요.",
        "keyword_in_meta_desc": f"메타 설명에 '{focus_kw}' 포함시키세요.",
        "keyword_in_intro": f"본문 첫 10%에 '{focus_kw}'를 추가하세요.",
        "content_length": "본문 2500자 이상으로 늘리세요.",
        "keyword_in_content": f"본문에 '{focus_kw}'를 추가하세요.",
        "internal_links": "내부 링크 1개 이상 추가하세요. wp_find_internal_links 사용.",
        "seo_title_set": f"SEO 제목을 설정하세요. wp_update_post(post_id={post_id}, seo_title='제목') 사용.",
        "title_length": "SEO 제목을 60자 이하로 줄이세요.",
        "title_starts_with_kw": f"SEO 제목을 '{focus_kw}'로 시작하세요.",
        "title_has_number": "제목에 숫자를 포함시키세요 (예: 7가지, 5단계).",
        "faq_schema": "FAQ JSON-LD 스키마를 추가하세요.",
        "url_length": "URL 슬러그를 75자 이하로 줄이세요 (한국어 인코딩 주의).",
    }
    for name, instruction in other_checks.items():
        if name in failed and name not in ["keyword_in_url", "has_images", "short_paragraphs", "h2_structure", "keyword_density", "meta_desc_length", "external_links", "keyword_in_headings"]:
            manual_needed.append((name, instruction))

    # ── 5단계: 재점수 ──
    seo_after = _compute_seo_score(post_id)
    after_score = seo_after["score"] if seo_after else "?"
    after_failed = [c for c in seo_after.get("checks", []) if not c["passed"]] if seo_after else []

    # ── 리포트 출력 ──
    if auto_fixed:
        lines.append("### ✅ 자동 수정 완료")
        for f in auto_fixed:
            lines.append(f"- {f}")
        lines.append("")

    lines.append(f"### 점수: {before_score} → {after_score}/100\n")

    if manual_needed:
        lines.append("### 📋 Claude가 수정할 항목")
        lines.append("아래 항목을 순서대로 수정하고 `wp_update_post`로 업데이트하세요.\n")
        for i, (name, instruction) in enumerate(manual_needed, 1):
            lines.append(f"**{i}. {name}**")
            lines.append(f"{instruction}\n")

    if after_failed:
        check_labels = {
            'keyword_in_seo_title': '키워드→SEO제목', 'keyword_in_meta_desc': '키워드→메타설명',
            'keyword_in_url': '키워드→URL', 'keyword_in_intro': '키워드→도입부',
            'content_length': '본문길이', 'keyword_in_content': '키워드→본문',
            'keyword_in_headings': '키워드→소제목', 'keyword_density': '키워드밀도',
            'has_images': '이미지', 'url_length': 'URL길이', 'internal_links': '내부링크',
            'external_links': '외부링크', 'title_length': '제목길이',
            'title_starts_with_kw': '제목키워드시작', 'title_has_number': '제목숫자',
            'meta_desc_length': '메타설명길이', 'short_paragraphs': '문단길이',
            'faq_schema': 'FAQ스키마', 'h2_structure': 'H2구조',
        }
        lines.append("### 남은 실패 항목")
        for c in after_failed:
            label = check_labels.get(c["name"], c["name"])
            lines.append(f"  ❌ {label} (w:{c['weight']})")

    if not manual_needed and not after_failed:
        lines.append("🎉 모든 SEO 항목 통과!")

    return "\n".join(lines)


# ── 도구 18: 스타일 DNA 추출 ─────────────────────────────

@mcp.tool()
def wp_extract_style_dna(count: int = 5) -> str:
    """기존 발행 글에서 스타일 DNA를 추출합니다.

    최근 N개 글을 분석하여 문체 프로필 + 스타일 가이드 + few-shot 샘플을 생성합니다.
    새 글 작성 시 이 결과를 프롬프트에 주입하면 기존 블로그 톤에 맞는 글이 생성됩니다.

    반환 내용:
    1. 문체 프로필 (문단/문장 길이, 어투 비율, 구조 패턴)
    2. 스타일 가이드 (도출된 규칙)
    3. Few-shot 샘플 (대표 문단 3개)

    Args:
        count: 분석할 최근 글 수 (기본 5, 최대 10)
    """
    count = max(1, min(count, 10))

    # ── 글 가져오기 ──
    try:
        r = _wp_get("posts", {"per_page": count, "orderby": "date", "order": "desc", "status": "publish"})
        if r.status_code != 200:
            return f"❌ 글 목록 조회 실패: HTTP {r.status_code}"
        posts = r.json()
        if not posts:
            return "❌ 발행된 글이 없습니다. 최소 1개 이상의 글이 필요합니다."
    except Exception as e:
        return f"❌ 글 조회 실패: {e}"

    # ── 분석 데이터 수집 ──
    all_para_lengths: list[int] = []
    all_sent_lengths: list[int] = []
    first_person_counts: list[int] = []
    colloquial_counts: list[int] = []
    digression_counts: list[int] = []
    h2_counts: list[int] = []
    h3_counts: list[int] = []
    word_counts: list[int] = []
    best_paragraphs: list[tuple[float, str, str]] = []  # (score, paragraph, post_title)
    section_openers: list[str] = []
    transition_words_found: dict[str, int] = {}

    first_person_patterns = [
        r"저는", r"제가", r"제\s", r"직접", r"해봤", r"해봤는데", r"써봤",
        r"경험상", r"느꼈", r"겪어", r"다녀", r"먹어봤", r"사용해\s?봤",
    ]
    colloquial_patterns = [
        "솔직히", "근데", "여담인데", "사실", "아무튼", "어쨌든",
        "그래서", "결국", "참고로", "덧붙이자면", "한마디로",
    ]
    digression_patterns = [
        r"여담", r"비유하자면", r"마치.*처럼", r"TMI", r"삽질",
        r"뻘짓", r"꿀팁", r"참고로", r"웃긴\s?건",
    ]

    for post in posts:
        html = post.get("content", {}).get("rendered", "")
        title = post.get("title", {}).get("rendered", "")
        if not html:
            continue

        # HTML → 텍스트 정리
        text_clean = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.S)
        text_clean = re.sub(r"<style[^>]*>.*?</style>", "", text_clean, flags=re.S)

        # 문단 추출
        paras_html = re.findall(r"<p\b[^>]*>(.*?)</p>", text_clean, re.S)
        paras = [re.sub(r"<[^>]+>", "", p).strip() for p in paras_html]
        paras = [p for p in paras if len(p) > 10]

        for p in paras:
            plen = len(p)
            all_para_lengths.append(plen)

            # 문장 분리
            sentences = re.split(r"[.!?。]\s*", p)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
            for s in sentences:
                all_sent_lengths.append(len(s))

            # few-shot 후보 채점: 1인칭 + 구어체 + 적절한 길이(80~250자) = 높은 점수
            p_score = 0.0
            for pat in first_person_patterns:
                if re.search(pat, p):
                    p_score += 2.0
            for coll in colloquial_patterns:
                if coll in p:
                    p_score += 1.5
            if 80 <= plen <= 250:
                p_score += 1.0
            if p_score > 0:
                best_paragraphs.append((p_score, p, title))

        # H2/H3 개수
        h2s = re.findall(r"<h2[^>]*>(.*?)</h2>", text_clean, re.S)
        h3s = re.findall(r"<h3[^>]*>(.*?)</h3>", text_clean, re.S)
        h2_counts.append(len(h2s))
        h3_counts.append(len(h3s))

        # 섹션 도입부 패턴 (H2 바로 다음 문단의 첫 어절)
        h2_para_pairs = re.findall(r"</h2>\s*<p[^>]*>(.*?)</p>", text_clean, re.S)
        for hp in h2_para_pairs:
            opener_text = re.sub(r"<[^>]+>", "", hp).strip()
            if opener_text:
                first_word = opener_text.split()[0] if opener_text.split() else ""
                if first_word:
                    section_openers.append(first_word)

        # 전체 텍스트
        full_text = re.sub(r"<[^>]+>", "", text_clean).strip()
        word_counts.append(len(full_text))

        # 1인칭
        fp_count = 0
        for pat in first_person_patterns:
            fp_count += len(re.findall(pat, full_text))
        first_person_counts.append(fp_count)

        # 구어체
        coll_count = 0
        for coll in colloquial_patterns:
            cnt = full_text.count(coll)
            coll_count += cnt
            if cnt > 0:
                transition_words_found[coll] = transition_words_found.get(coll, 0) + cnt
        colloquial_counts.append(coll_count)

        # 여담/비유
        dig_count = 0
        for pat in digression_patterns:
            dig_count += len(re.findall(pat, full_text))
        digression_counts.append(dig_count)

    # ── 통계 계산 ──
    def avg(lst):
        return sum(lst) / len(lst) if lst else 0

    def stdev(lst):
        if len(lst) < 2:
            return 0
        m = avg(lst)
        return (sum((x - m) ** 2 for x in lst) / len(lst)) ** 0.5

    avg_para = avg(all_para_lengths)
    std_para = stdev(all_para_lengths)
    cv_para = std_para / avg_para if avg_para > 0 else 0
    avg_sent = avg(all_sent_lengths)
    avg_fp = avg(first_person_counts)
    avg_coll = avg(colloquial_counts)
    avg_dig = avg(digression_counts)
    avg_h2 = avg(h2_counts)
    avg_words = avg(word_counts)

    # 섹션 도입부 다양성
    opener_unique_ratio = len(set(section_openers)) / len(section_openers) if section_openers else 1.0

    # ── 결과 포맷 ──
    lines = [f"# 스타일 DNA 분석 ({len(posts)}개 글 기준)\n"]

    # 1. 문체 프로필
    lines.append("## 1. 문체 프로필\n")
    lines.append(f"| 지표 | 값 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 평균 글 길이 | {avg_words:.0f}자 |")
    lines.append(f"| 평균 문단 길이 | {avg_para:.0f}자 (표준편차: {std_para:.0f}) |")
    lines.append(f"| 문단 변동계수 | {cv_para:.2f} {'✅ 자연스러움' if cv_para >= 0.4 else '⚠️ 균일함'} |")
    lines.append(f"| 평균 문장 길이 | {avg_sent:.0f}자 |")
    lines.append(f"| 평균 H2 소제목 수 | {avg_h2:.1f}개 |")
    lines.append(f"| 1인칭 표현 (글당 평균) | {avg_fp:.1f}회 |")
    lines.append(f"| 구어체 전환어 (글당 평균) | {avg_coll:.1f}회 |")
    lines.append(f"| 여담/비유 (글당 평균) | {avg_dig:.1f}회 |")
    lines.append(f"| 섹션 도입부 다양성 | {opener_unique_ratio:.0%} |")

    if transition_words_found:
        top_trans = sorted(transition_words_found.items(), key=lambda x: -x[1])[:8]
        trans_str = ", ".join(f"{w}({c})" for w, c in top_trans)
        lines.append(f"| 자주 쓰는 전환어 | {trans_str} |")

    # 2. 스타일 가이드
    lines.append("\n## 2. 스타일 가이드 (프롬프트 주입용)\n")
    lines.append("```")
    lines.append("## 문체 규칙 — 이 블로그의 스타일을 따라 작성하세요\n")

    # 문단 구조
    short_threshold = int(avg_para * 0.5)
    long_threshold = int(avg_para * 1.5)
    lines.append(f"1. 문단 길이를 다양하게: 짧은 문단({short_threshold}자 이하)과 긴 문단({long_threshold}자 내외)을 섞어 쓰세요.")
    lines.append(f"2. 평균 문단 길이는 {avg_para:.0f}자 내외로 유지하되, 변동계수 0.4 이상이 되도록 길이를 다양하게.")

    # 어투
    if avg_fp >= 3:
        lines.append(f"3. 1인칭 표현을 글당 {avg_fp:.0f}회 이상 사용: \"저는\", \"직접\", \"해봤\", \"경험상\" 등.")
    elif avg_fp >= 1:
        lines.append(f"3. 1인칭 표현을 글당 {avg_fp:.0f}~{avg_fp+2:.0f}회 사용: \"저는\", \"직접 해봤\", \"경험상\" 등.")
    else:
        lines.append("3. 1인칭 표현은 거의 사용하지 않는 스타일. 객관적 톤 유지.")

    if avg_coll >= 2:
        lines.append(f"4. 구어체 전환어를 글당 {avg_coll:.0f}회 이상 사용: \"솔직히\", \"근데\", \"사실\", \"아무튼\" 등.")
    else:
        lines.append("4. 구어체 전환어는 최소한으로. 비교적 정제된 문체.")

    if avg_dig >= 1:
        lines.append(f"5. 여담이나 비유를 글당 {avg_dig:.0f}회 이상 넣어 인간미 부여: \"여담인데\", \"삽질\", \"마치~처럼\" 등.")

    # 구조
    lines.append(f"6. H2 소제목은 {max(3, int(avg_h2 - 1))}~{int(avg_h2 + 2)}개 사용.")
    lines.append(f"7. 글 전체 길이는 {avg_words:.0f}자 내외.")
    lines.append("8. 섹션 도입부를 매번 다르게 시작. 같은 단어로 연속 시작 금지.")
    lines.append("9. 문장 시작 단어를 다양하게. 반복 패턴을 피하세요.")
    lines.append("```")

    # 3. Few-shot 샘플
    lines.append("\n## 3. Few-shot 샘플 (대표 문단)\n")
    lines.append("아래는 기존 글에서 추출한 스타일이 잘 드러나는 문단입니다. 이 톤과 구조를 참고하세요.\n")

    # 점수 높은 순 정렬, 상위 3개 (중복 글 방지)
    best_paragraphs.sort(key=lambda x: -x[0])
    selected = []
    seen_titles = set()
    for score, para, ptitle in best_paragraphs:
        if ptitle in seen_titles and len(selected) >= 2:
            continue
        selected.append((para, ptitle))
        seen_titles.add(ptitle)
        if len(selected) >= 3:
            break

    if selected:
        for i, (para, ptitle) in enumerate(selected, 1):
            lines.append(f"**샘플 {i}** (출처: {ptitle})")
            lines.append(f"> {para}\n")
    else:
        lines.append("(1인칭/구어체 표현이 포함된 문단을 찾지 못했습니다. 기존 글에 이런 표현을 추가하면 더 좋은 스타일 가이드가 생성됩니다.)\n")

    # 4. 사용법 안내
    lines.append("---")
    lines.append("## 사용법\n")
    lines.append("새 글 작성 시 위 **스타일 가이드**와 **Few-shot 샘플**을 프롬프트에 포함하세요:")
    lines.append("1. `wp_extract_style_dna()` 호출 → 스타일 가이드 획득")
    lines.append("2. 스타일 가이드 + 주제/키워드를 결합하여 글 작성")
    lines.append("3. `wp_style_check()` 호출 → 문체 자연스러움 검증")
    lines.append("4. `wp_seo_check()` 호출 → SEO 최적화 확인")

    return "\n".join(lines)


# ── 도구 17: 스타일 체크 ──────────────────────────────────

@mcp.tool()
def wp_style_check(content: str) -> str:
    """생성된 글이 자연스러운 문체인지 검증합니다.

    AI가 생성한 글의 문체 자연스러움을 체크합니다:
    - 문단 길이 분포 (표준편차가 낮으면 AI스러움 경고)
    - 1인칭 표현 횟수 (최소 3회 권장)
    - 구어체 전환어 사용 횟수
    - 연속 동일 구조 반복 여부
    - 문장 시작 다양성

    Args:
        content: HTML 본문
    """
    content_text = re.sub(r"<[^>]+>", "", content).strip()
    lines_out = ["## 문체 스타일 체크\n"]
    score = 0
    total = 0
    suggestions = []

    # ── 1. 문단 길이 분포 ──
    total += 1
    paragraphs = re.findall(r"<p\b[^>]*>(.*?)</p>", content, re.DOTALL | re.IGNORECASE)
    p_lengths = [len(re.sub(r"<[^>]+>", "", p).strip()) for p in paragraphs if len(re.sub(r"<[^>]+>", "", p).strip()) > 5]

    if len(p_lengths) >= 3:
        avg_len = sum(p_lengths) / len(p_lengths)
        variance = sum((l - avg_len) ** 2 for l in p_lengths) / len(p_lengths)
        std_dev = variance ** 0.5
        cv = std_dev / avg_len if avg_len > 0 else 0  # 변동계수

        short_p = sum(1 for l in p_lengths if l < 50)
        long_p = sum(1 for l in p_lengths if l > 200)

        if cv >= 0.4 and short_p >= 1:
            score += 1
            lines_out.append(f"✅ 문단 길이 다양성 — 변동계수 {cv:.2f}, 짧은 문단 {short_p}개, 긴 문단 {long_p}개")
        else:
            lines_out.append(f"❌ 문단 길이 균일 (AI 패턴) — 변동계수 {cv:.2f}")
            if short_p == 0:
                suggestions.append(
                    "### 짧은 문단 추가\n"
                    "모든 문단이 비슷한 길이입니다. 1~2문장짜리 짧은 문단을 섞으세요.\n"
                    "예: 핵심 주장을 한 줄로 강조하거나, 전환 문장을 독립 문단으로 분리"
                )
    else:
        lines_out.append(f"⚪ 문단 수 부족 ({len(p_lengths)}개) — 분석 불가")

    # ── 2. 1인칭 표현 ──
    total += 1
    first_person_patterns = [
        r"저는\s", r"제가\s", r"저의\s", r"저도\s",
        r"제\s경험", r"직접\s", r"실제로\s",
        r"해봤", r"써봤", r"경험했", r"느꼈",
        r"해보니", r"써보니", r"겪어보",
        r"개인적으로", r"솔직히\s말하",
    ]
    fp_count = 0
    for pattern in first_person_patterns:
        fp_count += len(re.findall(pattern, content_text))

    if fp_count >= 3:
        score += 1
        lines_out.append(f"✅ 1인칭 경험 표현 — {fp_count}회 (3회 이상)")
    else:
        lines_out.append(f"❌ 1인칭 경험 표현 부족 — {fp_count}회 (최소 3회 권장)")
        suggestions.append(
            "### 1인칭 경험담 추가\n"
            f"현재 {fp_count}회. 최소 3회 이상 삽입하세요.\n"
            "예시:\n"
            '  - "저는 이걸 처음 써봤을 때..."\n'
            '  - "직접 테스트해보니 결과가..."\n'
            '  - "제 경험상 이 방법이 가장..."'
        )

    # ── 3. 구어체 전환어 ──
    total += 1
    colloquial_patterns = [
        r"솔직히", r"근데", r"아\s그리고", r"사실\s",
        r"이건\s좀", r"좀\s짜증", r"진짜\s", r"여담인데",
        r"참고로", r"그런데\s말이죠", r"아무튼",
        r"한마디로", r"결론부터\s말하면", r"간단히\s말해",
        r"쉽게\s말해", r"다시\s말하면",
    ]
    coll_count = 0
    coll_found = []
    for pattern in colloquial_patterns:
        matches = re.findall(pattern, content_text)
        if matches:
            coll_count += len(matches)
            coll_found.append(matches[0])

    if coll_count >= 2:
        score += 1
        found_str = ", ".join(coll_found[:5])
        lines_out.append(f"✅ 구어체 전환어 — {coll_count}회 ({found_str})")
    else:
        lines_out.append(f"❌ 구어체 전환어 부족 — {coll_count}회 (2회 이상 권장)")
        suggestions.append(
            "### 구어체 전환어 추가\n"
            "자연스러운 전환 표현을 섞으세요:\n"
            '  - "솔직히 이건 좀 놀라웠습니다"\n'
            '  - "근데 여기서 한 가지 주의할 점이..."\n'
            '  - "여담인데 이거 처음 해봤을 때..."\n'
            '  - "사실 이 부분이 가장 중요합니다"'
        )

    # ── 4. 구조 반복 패턴 ──
    total += 1
    # H2 뒤에 오는 첫 문장의 시작 패턴을 비교
    h2_sections = re.findall(r"<h2[^>]*>.*?</h2>\s*<p[^>]*>(.*?)</p>", content, re.DOTALL | re.IGNORECASE)
    if len(h2_sections) >= 3:
        first_words = []
        for section in h2_sections:
            text = re.sub(r"<[^>]+>", "", section).strip()
            words = text.split()[:3]
            first_words.append(" ".join(words) if words else "")

        # 연속 3개 이상이 같은 패턴으로 시작하는지
        repeated = 0
        for i in range(len(first_words) - 2):
            # 첫 단어가 같으면 반복 패턴
            w1 = first_words[i].split()[0] if first_words[i] else ""
            w2 = first_words[i + 1].split()[0] if first_words[i + 1] else ""
            w3 = first_words[i + 2].split()[0] if first_words[i + 2] else ""
            if w1 and w1 == w2 == w3:
                repeated += 1

        if repeated == 0:
            score += 1
            lines_out.append(f"✅ 섹션 도입 다양성 — 반복 패턴 없음")
        else:
            lines_out.append(f"❌ 섹션 도입 반복 — {repeated}곳에서 동일 패턴")
            suggestions.append(
                "### 섹션 도입부 다양화\n"
                "연속 섹션이 같은 방식으로 시작합니다. 다양한 도입을 쓰세요:\n"
                "  - 질문으로: \"~해본 적 있으신가요?\"\n"
                "  - 경험담으로: \"저는 이때 ~했습니다\"\n"
                "  - 결론 먼저: \"결론부터 말하면 ~입니다\"\n"
                "  - 상황 묘사: \"서버가 터지고 30분이 지났을 때...\""
            )
    else:
        lines_out.append(f"⚪ H2 섹션 부족 ({len(h2_sections)}개) — 구조 분석 불가")

    # ── 5. 문장 시작 다양성 ──
    total += 1
    sentences = re.split(r"[.!?]\s+", content_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    if len(sentences) >= 5:
        first_chars = [s[0] if s else "" for s in sentences]
        unique_ratio = len(set(first_chars)) / len(first_chars) if first_chars else 0
        if unique_ratio >= 0.5:
            score += 1
            lines_out.append(f"✅ 문장 시작 다양성 — 고유 비율 {unique_ratio:.0%}")
        else:
            lines_out.append(f"❌ 문장 시작 단조로움 — 고유 비율 {unique_ratio:.0%}")
            suggestions.append(
                "### 문장 시작 다양화\n"
                "문장이 너무 비슷하게 시작합니다. 다양한 시작을 쓰세요:\n"
                "  - 부사: \"실제로\", \"결국\", \"특히\"\n"
                "  - 접속사: \"하지만\", \"그래서\", \"반면에\"\n"
                "  - 명사: 주어를 바꿔가며\n"
                "  - 의문문: \"왜 이렇게 될까요?\""
            )
    else:
        lines_out.append(f"⚪ 문장 수 부족 ({len(sentences)}개) — 분석 불가")

    # ── 6. 여담/비유 표현 ──
    total += 1
    digression_patterns = [
        r"여담", r"비유하자면", r"비유로", r"마치\s.*처럼",
        r"참고로\s말씀드리", r"TMI", r"덧붙이자면",
        r"한\s가지\s재미있는", r"사족을\s붙이자면",
    ]
    dig_count = sum(len(re.findall(p, content_text)) for p in digression_patterns)
    if dig_count >= 1:
        score += 1
        lines_out.append(f"✅ 여담/비유 — {dig_count}회")
    else:
        lines_out.append(f"❌ 여담/비유 없음 — 0회 (1회 이상 권장)")
        suggestions.append(
            "### 여담 또는 비유 추가\n"
            "중간에 여담이나 비유를 1~2개 넣으세요:\n"
            '  - "여담인데, 이거 처음 해봤을 때 30분 동안 삽질했습니다"\n'
            '  - "마치 레고 블록을 조립하는 것처럼..."\n'
            '  - "TMI지만 이 도구는 제가 가장 좋아하는..."'
        )

    # ── 점수 계산 ──
    pct = int((score / total) * 100) if total > 0 else 0
    if pct >= 80:
        grade = "🟢 자연스러움"
    elif pct >= 50:
        grade = "🟡 개선 가능"
    else:
        grade = "🔴 AI 패턴 감지"

    header_line = f"**스타일 점수: {score}/{total} ({pct}%) {grade}**\n"
    lines_out.insert(1, header_line)

    # ── 수정 제안 ──
    if suggestions:
        lines_out.append(f"\n---\n## 스타일 수정 제안 ({len(suggestions)}개)\n")
        lines_out.append("\n\n".join(suggestions))

    return "\n".join(lines_out)


# ── 엔트리포인트 ─────────────────────────────────────────

def main():
    mcp.run()


if __name__ == "__main__":
    main()
