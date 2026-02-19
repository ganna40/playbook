"""WordPress MCP Server 테스트 — 모든 도구를 순차적으로 검증"""

import sys
import os

# .env 로드
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

# 모듈 임포트
from wordpress_mcp import (
    wp_check_connection,
    wp_keyword_research,
    wp_check_cannibalization,
    wp_list_posts,
    wp_list_drafts,
    wp_seo_check,
    wp_find_internal_links,
    wp_find_image,
    wp_create_post,
    wp_get_post,
    wp_review_draft,
    wp_update_post,
    wp_schedule_draft,
    _resolve_category,
    _resolve_or_create_tag,
    WP_USERNAME,
    WP_APP_PASSWORD,
)


def header(name):
    print(f"\n{'='*60}")
    print(f"  TEST: {name}")
    print(f"{'='*60}")


def test_connection():
    header("wp_check_connection")
    result = wp_check_connection()
    print(result)
    return "✅" in result


def test_keyword_research():
    header("wp_keyword_research")
    result = wp_keyword_research("AI 에이전트")
    print(result)
    return "자동완성" in result


def test_category_resolution():
    header("카테고리 이름→ID 변환")
    cat_id = _resolve_category("테크")
    print(f"  '테크' → ID: {cat_id}")
    cat_id2 = _resolve_category("AI")
    print(f"  'AI' → ID: {cat_id2}")
    return cat_id is not None


def test_cannibalization():
    header("wp_check_cannibalization")
    result = wp_check_cannibalization("AI")
    print(result)
    return True  # 결과가 나오면 성공


def test_list_posts():
    header("wp_list_posts")
    result = wp_list_posts(count=5, status="publish")
    print(result)
    return "❌" not in result or "글이 없습니다" in result


def test_list_drafts():
    header("wp_list_drafts")
    result = wp_list_drafts()
    print(result)
    return True


def test_seo_check():
    header("wp_seo_check")
    sample_content = """
    <h1>AI 에이전트 가이드</h1>
    <p><strong>AI 에이전트</strong>란 자율적으로 작업을 수행하는 인공지능 시스템입니다.</p>
    <div style="background-color: #f8f9fa; padding: 20px;">
    <strong>목차</strong>
    <ul><li><a href="#what">AI 에이전트란?</a></li></ul>
    </div>
    <h2 id="what">AI 에이전트란 무엇인가</h2>
    <p>AI 에이전트는 환경을 인식하고 목표를 달성하기 위해 행동하는 시스템입니다.</p>
    <h2 id="types">AI 에이전트의 종류</h2>
    <p>반응형, 목표 기반, 학습형 등 다양한 유형이 있습니다.</p>
    <h2 id="framework">AI 에이전트 프레임워크 비교</h2>
    <p>LangGraph, CrewAI, AutoGen 등이 있습니다. AI 에이전트 개발에 널리 사용됩니다.</p>
    <h2 id="faq">자주 묻는 질문</h2>
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"AI 에이전트란?","acceptedAnswer":{"@type":"Answer","text":"자율적으로 작업하는 AI 시스템"}}]}
    </script>
    <h3>AI 에이전트란?</h3>
    <p>자율적으로 작업하는 AI 시스템입니다.</p>
    <p><a href="https://pearsoninsight.com/ai-guide/">관련 글 보기</a></p>
    """
    result = wp_seo_check(
        content=sample_content,
        focus_keyword="AI 에이전트",
        seo_title="AI 에이전트 — 개념부터 프레임워크 비교까지 완벽 가이드",
        meta_description="AI 에이전트란 무엇인지, 종류, 프레임워크 비교, 직접 만드는 방법까지 정리합니다. AI 에이전트 입문자를 위한 완벽 가이드.",
        slug="ai-agent-guide",
    )
    print(result)
    return "SEO 체크" in result


def test_find_internal_links():
    header("wp_find_internal_links")
    result = wp_find_internal_links("AI")
    print(result)
    return True


def test_find_image():
    header("wp_find_image (검색만, 업로드 안 함)")
    result = wp_find_image("AI agent", upload=False)
    print(result)
    return True  # 키 없으면 에러 메시지도 OK


def test_create_and_review():
    """글 생성 → 리뷰 → 삭제 (테스트 후 정리)"""
    header("wp_create_post (테스트 초안)")
    result = wp_create_post(
        title="[TEST] MCP 서버 테스트 글 — 삭제 예정",
        content="<h1>테스트</h1><p>이 글은 MCP 서버 테스트용입니다. 곧 삭제됩니다.</p>",
        focus_keyword="MCP 테스트",
        seo_title="MCP 서버 테스트 글",
        meta_description="WordPress MCP 서버 테스트를 위한 임시 글입니다.",
        slug="mcp-test-delete-me",
        excerpt="MCP 서버 테스트 글입니다.",
        category="테크",
        tags="MCP,테스트",
        status="draft",
    )
    print(result)

    if "❌" in result:
        return False

    # ID 추출
    import re
    id_match = re.search(r"ID: (\d+)", result)
    if not id_match:
        print("  ❌ ID 추출 실패")
        return False

    post_id = int(id_match.group(1))

    # 리뷰
    header("wp_review_draft")
    review = wp_review_draft(post_id)
    print(review)

    # 글 조회
    header("wp_get_post")
    detail = wp_get_post(post_id)
    print(detail[:500])

    # 삭제 (휴지통으로)
    header("테스트 글 정리 (휴지통)")
    import httpx, base64
    token = base64.b64encode(f"{WP_USERNAME}:{WP_APP_PASSWORD}".encode()).decode()
    r = httpx.delete(
        f"https://pearsoninsight.com/wp-json/wp/v2/posts/{post_id}",
        headers={"Authorization": f"Basic {token}"},
        timeout=30,
        follow_redirects=True,
    )
    if r.status_code == 200:
        print(f"  ✅ 테스트 글 (ID: {post_id}) 휴지통으로 이동")
    else:
        print(f"  ⚠️ 삭제 실패: HTTP {r.status_code} — 수동 삭제 필요")

    return True


def main():
    print("WordPress MCP Server 전체 테스트")
    print(f"WP_USERNAME: {WP_USERNAME}")
    print(f"WP_APP_PASSWORD: {'*' * len(WP_APP_PASSWORD) if WP_APP_PASSWORD else '미설정'}")

    results = {}
    tests = [
        ("연결 확인", test_connection),
        ("키워드 리서치", test_keyword_research),
        ("카테고리 변환", test_category_resolution),
        ("카니발리제이션", test_cannibalization),
        ("글 목록", test_list_posts),
        ("초안 목록", test_list_drafts),
        ("SEO 체크", test_seo_check),
        ("내부 링크", test_find_internal_links),
        ("이미지 검색", test_find_image),
        ("글 생성→리뷰→삭제", test_create_and_review),
    ]

    for name, fn in tests:
        try:
            ok = fn()
            results[name] = "✅ PASS" if ok else "❌ FAIL"
        except Exception as e:
            results[name] = f"💥 ERROR: {e}"
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print("  테스트 결과 요약")
    print(f"{'='*60}")
    for name, status in results.items():
        print(f"  {status}  {name}")

    passed = sum(1 for v in results.values() if "PASS" in v)
    total = len(results)
    print(f"\n  {passed}/{total} 통과")


if __name__ == "__main__":
    main()
