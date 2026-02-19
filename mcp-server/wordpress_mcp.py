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


# ── 도구 9: SEO 체크 ─────────────────────────────────────

@mcp.tool()
def wp_seo_check(content: str, focus_keyword: str, seo_title: str = "", meta_description: str = "", slug: str = "") -> str:
    """RankMath 기준에 맞춘 SEO 체크 (MCP 자체 분석, RankMath 실제 점수는 WP 에디터에서 확인).

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
    # 연속 공백 정리
    content_text = re.sub(r"\s+", " ", content_text)
    content_text_lower = content_text.lower()
    char_count = len(content_text)
    word_count = len(content_text.split())

    checks = []
    score = 0
    total = 0

    def check(name: str, passed: bool, weight: int = 1, detail: str = ""):
        nonlocal score, total
        total += weight
        if passed:
            score += weight
        icon = "✅" if passed else "❌"
        msg = f"{icon} {name}"
        if detail:
            msg += f" — {detail}"
        checks.append(msg)

    # ── 기본 SEO (RankMath: Basic SEO) ────────────────────

    checks.append("\n**[기본 SEO]**")

    # 1. 포커스 키워드가 SEO 제목에 포함
    check("포커스 키워드가 SEO 제목에 포함", kw in (seo_title or "").lower(), 2)

    # 2. 포커스 키워드가 메타 설명에 포함
    if meta_description:
        check("포커스 키워드가 메타 설명에 포함", kw in meta_description.lower(), 2)
    else:
        check("메타 설명 설정", False, 2, "미설정")

    # 3. 포커스 키워드가 URL에 포함
    if slug:
        kw_parts = kw.split()
        slug_lower = slug.lower()
        check("포커스 키워드가 URL에 포함", any(p in slug_lower for p in kw_parts), 2)
    else:
        check("URL 슬러그 설정", False, 2, "미설정")

    # 4. 포커스 키워드가 본문 첫 10%에 포함
    first_10pct = content_text_lower[:max(len(content_text_lower) // 10, 200)]
    check("포커스 키워드가 본문 도입부에 포함", kw in first_10pct, 2)

    # 5. 본문 길이 (RankMath: 600단어 이상 = 한국어로 ~2500자)
    check(f"본문 길이 ({char_count}자 / 약 {word_count}단어)", char_count >= 2500, 2, "RankMath 기준: 600단어+")

    # 6. 포커스 키워드가 본문에 포함
    check("포커스 키워드가 본문에 포함", kw in content_text_lower, 1)

    # ── 추가 SEO (RankMath: Additional) ───────────────────

    checks.append("\n**[추가 SEO]**")

    # 7. 포커스 키워드가 H2/H3/H4 소제목에 포함
    h_matches = re.findall(r"<h[2-4][^>]*>(.*?)</h[2-4]>", content, re.IGNORECASE)
    h_with_kw = sum(1 for h in h_matches if kw in h.lower())
    check(f"소제목(H2-H4)에 키워드 포함 ({h_with_kw}/{len(h_matches)}개)", h_with_kw >= 1, 2)

    # 8. 키워드 밀도 (RankMath: 1~2.5% 권장)
    if content_text_lower:
        kw_count = content_text_lower.count(kw)
        density = (kw_count * len(kw)) / len(content_text_lower) * 100
        in_range = 0.5 <= density <= 2.5
        check(f"키워드 밀도 ({density:.1f}%, {kw_count}회)", in_range, 2, "RankMath 기준: 1~2.5%")

    # 9. 이미지 alt에 키워드
    img_tags = re.findall(r"<img[^>]*>", content, re.IGNORECASE)
    img_alts = re.findall(r'alt=["\']([^"\']*)["\']', content, re.IGNORECASE)
    has_images = len(img_tags) > 0
    alt_with_kw = sum(1 for alt in img_alts if kw in alt.lower())
    if has_images:
        check(f"이미지 alt에 키워드 ({alt_with_kw}/{len(img_tags)})", alt_with_kw >= 1, 1)
    else:
        check("본문에 이미지 포함", False, 1, "이미지 없음 (대표이미지 별도)")

    # 10. URL 길이 (RankMath: 75자 이하)
    if slug:
        slug_len = len(slug)
        check(f"URL 길이 ({slug_len}자)", slug_len <= 75, 1, "RankMath 기준: 75자 이하")

    # 11. 내부 링크
    internal_links = re.findall(rf'href=["\']({re.escape(WP_URL)}[^"\']*)["\']', content, re.IGNORECASE)
    check(f"내부 링크 ({len(internal_links)}개)", len(internal_links) >= 1, 2, "최소 1개")

    # 12. 외부 링크 (RankMath: dofollow 외부 링크 최소 1개)
    all_links = re.findall(r'href=["\']([^"\']*)["\']', content, re.IGNORECASE)
    external_links = [l for l in all_links if l.startswith("http") and WP_URL not in l and not l.startswith("#")]
    check(f"외부 링크 ({len(external_links)}개)", len(external_links) >= 1, 1, "최소 1개 권장")

    # ── 제목 가독성 (RankMath: Title Readability) ─────────

    checks.append("\n**[제목 가독성]**")

    # 13. SEO 제목 길이
    if seo_title:
        st_len = len(seo_title)
        check(f"SEO 제목 길이 ({st_len}자)", 30 <= st_len <= 60, 1, "RankMath 기준: 60자 이하")
    else:
        check("SEO 제목 설정", False, 1, "미설정")

    # 14. 제목이 키워드로 시작
    if seo_title:
        check("제목이 키워드로 시작", (seo_title or "").lower().startswith(kw), 1, "SEO 가산점")

    # 15. 제목에 숫자 포함
    if seo_title:
        has_number = bool(re.search(r"\d", seo_title))
        check("제목에 숫자 포함", has_number, 1, "CTR 향상")

    # ── 콘텐츠 가독성 (RankMath: Content Readability) ─────

    checks.append("\n**[콘텐츠 가독성]**")

    # 16. 메타 설명 길이
    if meta_description:
        md_len = len(meta_description)
        check(f"메타 설명 길이 ({md_len}자)", 120 <= md_len <= 160, 1, "RankMath 기준: 120~160자")

    # 17. 짧은 단락 (RankMath: 120단어 이하 단락)
    paragraphs = re.findall(r"<p[^>]*>(.*?)</p>", content, re.DOTALL | re.IGNORECASE)
    long_paragraphs = [p for p in paragraphs if len(re.sub(r"<[^>]+>", "", p).strip()) > 300]
    check(f"짧은 단락 ({len(long_paragraphs)}개 > 300자)", len(long_paragraphs) == 0, 1, "긴 단락 분리 권장")

    # 18. 미디어 포함 (이미지/비디오)
    has_media = bool(img_tags) or "<video" in content_lower or "<iframe" in content_lower
    check("미디어(이미지/비디오) 포함", has_media, 1)

    # ── 추가 품질 체크 ────────────────────────────────────

    checks.append("\n**[추가 품질]**")

    # FAQ 스키마
    has_faq_schema = "application/ld+json" in content_lower and "faqpage" in content_lower
    check("FAQ JSON-LD 스키마", has_faq_schema, 1)

    # H2 구조
    h2_matches = re.findall(r"<h2[^>]*>(.*?)</h2>", content, re.IGNORECASE)
    check(f"H2 소제목 구조 ({len(h2_matches)}개)", 3 <= len(h2_matches) <= 8, 1, "3~8개 권장")

    # ── 점수 계산 ─────────────────────────────────────────
    pct = int((score / total) * 100) if total > 0 else 0

    if pct >= 80:
        grade = "🟢 Good"
    elif pct >= 60:
        grade = "🟡 개선 권장"
    else:
        grade = "🔴 수정 필수"

    header = f"## MCP SEO 체크: {pct}/100 {grade}"
    header += f"\n⚠️ RankMath 실제 점수는 WP 에디터에서 확인하세요.\n"
    return header + "\n".join(checks)


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


# ── 도구 12: 내부 링크 추천 ──────────────────────────────

@mcp.tool()
def wp_find_internal_links(focus_keyword: str) -> str:
    """기존 글 중 관련 글을 찾아서 내부 링크 후보를 추천합니다.

    Args:
        focus_keyword: 현재 글의 포커스 키워드
    """
    kw_words = set(focus_keyword.lower().split())
    suggestions = []

    try:
        # 키워드 관련 글 검색
        r = _wp_get("posts", {"per_page": 30, "search": focus_keyword, "status": "publish"})
        if r.status_code == 200:
            for post in r.json():
                title = post["title"]["rendered"]
                title_lower = title.lower()
                # 키워드 단어 매칭 점수
                match_score = sum(1 for w in kw_words if w in title_lower)
                if match_score > 0:
                    suggestions.append({
                        "score": match_score,
                        "title": title,
                        "url": post["link"],
                        "slug": post["slug"],
                    })

        # 점수순 정렬
        suggestions.sort(key=lambda x: x["score"], reverse=True)
        suggestions = suggestions[:5]
    except Exception as e:
        return f"❌ 내부 링크 검색 실패: {e}"

    if not suggestions:
        return f"'{focus_keyword}' 관련 기존 글을 찾을 수 없습니다."

    lines = [f"## 내부 링크 추천 ({len(suggestions)}개)\n"]
    for s in suggestions:
        lines.append(f"- **{s['title']}**")
        lines.append(f"  URL: {s['url']}")
        lines.append(f"  HTML: `<a href=\"{s['url']}\">{s['title']}</a>`")
    lines.append(f"\n💡 본문 하단에 관련 글 박스로 삽입하세요.")
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


# ── 엔트리포인트 ─────────────────────────────────────────

def main():
    mcp.run()


if __name__ == "__main__":
    main()
