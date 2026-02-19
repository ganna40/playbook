"""전체 파이프라인 테스트: 키워드 리서치 → SEO 글 작성 → draft 업로드 → 리뷰"""

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")

from wordpress_mcp import (
    wp_create_post,
    wp_seo_check,
    wp_review_draft,
    wp_find_internal_links,
)

# ── SEO 설계 ──────────────────────────────────────────────
FOCUS_KEYWORD = "Claude Code 활용법"
SEO_TITLE = "Claude Code 활용법 — 설치 후 진짜 써먹는 실전 팁 7가지 (2026)"
META_DESCRIPTION = "Claude Code 활용법을 정리합니다. 설치는 끝났는데 뭘 해야 할지 모르겠다면, 실전에서 바로 쓰는 7가지 활용 팁과 명령어를 확인하세요."
SLUG = "claude-code-tips-practical-guide"
EXCERPT = "Claude Code 설치 후 실전에서 바로 써먹는 활용법 7가지를 정리합니다. MCP 서버 연동, 슬래시 명령, Git 자동화까지."
CATEGORY = "테크"
TAGS = "Claude Code,AI 코딩,Claude,AI 자동화,MCP"

# ── HTML 본문 ─────────────────────────────────────────────
CONTENT = """
<h1>Claude Code 활용법 — 설치 후 진짜 써먹는 실전 팁 7가지 (2026)</h1>

<p><strong>Claude Code 활용법</strong>이 궁금하신가요? 설치는 했는데 터미널에서 뭘 해야 할지 막막했다면, 이 글이 정확히 그 답을 드립니다.</p>

<p>이 글에서는 Claude Code를 실무에서 바로 써먹을 수 있는 실전 팁 7가지를 소개합니다. 단순 코드 생성을 넘어서, 프로젝트 분석부터 Git 자동화, MCP 서버 연동까지 다룹니다.</p>

<div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
<strong>목차</strong>
<ul>
<li><a href="#what">Claude Code란?</a></li>
<li><a href="#tip1">1. /init으로 프로젝트 컨텍스트 잡기</a></li>
<li><a href="#tip2">2. CLAUDE.md로 나만의 규칙 설정하기</a></li>
<li><a href="#tip3">3. MCP 서버로 외부 도구 연결하기</a></li>
<li><a href="#tip4">4. 슬래시 명령어 활용하기</a></li>
<li><a href="#tip5">5. Git 워크플로우 자동화하기</a></li>
<li><a href="#tip6">6. 멀티 파일 리팩토링하기</a></li>
<li><a href="#tip7">7. Task 에이전트로 병렬 작업하기</a></li>
<li><a href="#faq">자주 묻는 질문</a></li>
</ul>
</div>

<h2 id="what">Claude Code란?</h2>

<p>Claude Code는 Anthropic이 만든 <strong>터미널 기반 AI 코딩 도구</strong>입니다. VS Code 같은 IDE가 아니라, 터미널에서 <code>claude</code> 명령어 하나로 실행되는 CLI 도구입니다.</p>

<p>기존 AI 코딩 도구(Cursor, Copilot)와 가장 큰 차이점은 <strong>에이전트 방식</strong>이라는 겁니다. 파일을 읽고, 수정하고, 테스트를 실행하고, Git 커밋까지 — Claude가 직접 터미널을 조작합니다.</p>

<h3>설치 확인</h3>

<p>아직 설치하지 않았다면 <code>npm install -g @anthropic-ai/claude-code</code>로 설치할 수 있습니다. 설치 후 <code>claude</code>를 입력하면 바로 대화가 시작됩니다.</p>

<h2 id="tip1">1. /init으로 프로젝트 컨텍스트 잡기</h2>

<p>Claude Code를 프로젝트 디렉토리에서 처음 실행하면 가장 먼저 해야 할 일이 있습니다. <code>/init</code> 명령어를 입력하세요.</p>

<p>이 명령어는 프로젝트의 구조를 분석해서 <strong>CLAUDE.md</strong> 파일을 자동 생성합니다. CLAUDE.md에는 프로젝트의 기술 스택, 디렉토리 구조, 빌드 명령어 등이 정리됩니다.</p>

<pre><code># 프로젝트 디렉토리에서
claude
> /init</code></pre>

<p>이렇게 하면 이후 모든 대화에서 Claude가 프로젝트 맥락을 이해한 상태로 답변합니다.</p>

<h2 id="tip2">2. CLAUDE.md로 나만의 규칙 설정하기</h2>

<p>CLAUDE.md는 Claude Code의 <strong>행동 규칙</strong>을 정의하는 파일입니다. 프로젝트 루트에 위치하며, Claude Code가 시작할 때마다 자동으로 읽습니다.</p>

<p>예를 들어 이런 규칙을 넣을 수 있습니다:</p>

<pre><code># CLAUDE.md 예시
- 모든 코드는 TypeScript로 작성
- 테스트는 vitest 사용
- 커밋 메시지는 한국어로 작성
- console.log 대신 logger 사용</code></pre>

<p>Claude Code 활용법에서 가장 중요한 포인트가 바로 이 CLAUDE.md 설정입니다. 한번 잘 만들어두면 매번 같은 말을 반복할 필요가 없습니다.</p>

<h2 id="tip3">3. MCP 서버로 외부 도구 연결하기</h2>

<p>MCP(Model Context Protocol)는 Claude Code에 <strong>외부 도구를 연결하는 표준 프로토콜</strong>입니다. 데이터베이스 조회, API 호출, 파일 변환 등 Claude가 직접 할 수 없는 작업을 MCP 서버를 통해 할 수 있습니다.</p>

<p>MCP 서버를 등록하는 방법:</p>

<pre><code># MCP 서버 추가
claude mcp add my-server -- python my_server.py

# 등록된 서버 확인
claude mcp list</code></pre>

<p>예를 들어 WordPress MCP 서버를 연결하면, "이 주제로 블로그 글 써서 올려줘"라는 한마디로 SEO 최적화된 글이 워드프레스에 올라갑니다.</p>

<h2 id="tip4">4. 슬래시 명령어 활용하기</h2>

<p>Claude Code에는 유용한 슬래시 명령어들이 있습니다:</p>

<table>
<thead><tr><th>명령어</th><th>설명</th></tr></thead>
<tbody>
<tr><td><code>/init</code></td><td>CLAUDE.md 자동 생성</td></tr>
<tr><td><code>/compact</code></td><td>대화 컨텍스트 압축 (토큰 절약)</td></tr>
<tr><td><code>/clear</code></td><td>대화 초기화</td></tr>
<tr><td><code>/cost</code></td><td>현재 세션 비용 확인</td></tr>
<tr><td><code>/help</code></td><td>도움말</td></tr>
<tr><td><code>/mcp</code></td><td>MCP 서버 상태 확인</td></tr>
</tbody>
</table>

<p>특히 <code>/compact</code>는 긴 작업을 할 때 필수입니다. 컨텍스트 윈도우가 커지면 속도가 느려지는데, 이 명령어로 핵심만 남기고 압축할 수 있습니다.</p>

<h2 id="tip5">5. Git 워크플로우 자동화하기</h2>

<p>Claude Code는 Git과 자연스럽게 통합됩니다. 코드를 수정한 뒤 "커밋해줘"라고 하면 변경사항을 분석해서 적절한 커밋 메시지를 작성하고, 스테이징부터 커밋까지 처리합니다.</p>

<pre><code># Claude Code에서
> 이 변경사항 커밋해줘
> PR 만들어줘
> 최근 커밋 로그 보여줘</code></pre>

<p>PR 생성도 가능합니다. <code>gh</code> CLI가 설치되어 있으면 Claude가 직접 GitHub PR을 만들고, 변경사항 요약까지 작성합니다.</p>

<h2 id="tip6">6. 멀티 파일 리팩토링하기</h2>

<p>Claude Code 활용법 중 가장 강력한 기능은 <strong>여러 파일을 동시에 수정</strong>하는 것입니다. "이 함수 이름을 getAllUsers에서 fetchUsers로 변경해줘"라고 하면, 관련된 모든 파일에서 참조를 찾아 한번에 수정합니다.</p>

<p>복잡한 리팩토링 예시:</p>

<pre><code>> src/api 폴더의 모든 API 함수에 에러 핸들링 추가해줘
> 이 프로젝트의 모든 console.log를 logger로 교체해줘
> 이 컴포넌트를 클래스형에서 함수형으로 변환해줘</code></pre>

<p>Claude Code는 먼저 관련 파일을 모두 읽고, 변경 계획을 세운 뒤, 파일별로 순차 수정합니다. 수동으로 하면 한 시간 걸릴 작업을 몇 분 만에 끝냅니다.</p>

<h2 id="tip7">7. Task 에이전트로 병렬 작업하기</h2>

<p>Claude Code에는 <strong>Task 도구</strong>가 있습니다. 독립적인 작업을 서브 에이전트에게 위임해서 병렬로 처리할 수 있습니다.</p>

<p>예를 들어 "이 프로젝트의 보안 취약점을 점검하고, 동시에 성능 최적화 포인트를 찾아줘"라고 하면, Claude가 두 개의 Task를 동시에 실행합니다.</p>

<p>Task 에이전트는 메인 컨텍스트를 오염시키지 않으면서 깊이 있는 조사를 할 수 있어서, 대규모 코드베이스 분석에 특히 유용합니다.</p>

<h2 id="summary">마무리</h2>

<p>Claude Code 활용법의 핵심은 단순 코드 생성이 아니라, <strong>프로젝트 전체를 이해하는 AI 동료</strong>로 쓰는 것입니다. CLAUDE.md로 규칙을 잡고, MCP로 도구를 연결하고, Task로 복잡한 작업을 위임하면 — 개발 생산성이 확실히 달라집니다.</p>

<p>지금 바로 프로젝트 디렉토리에서 <code>claude</code>를 실행하고, <code>/init</code>부터 시작해보세요.</p>

<h2 id="faq">자주 묻는 질문</h2>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Claude Code는 무료인가요?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Claude Code 자체는 무료로 설치할 수 있지만, API 사용량에 따라 비용이 발생합니다. Claude Pro나 Max 구독이 있으면 포함된 크레딧으로 사용할 수 있습니다."
      }
    },
    {
      "@type": "Question",
      "name": "Claude Code와 Cursor의 차이점은?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Cursor는 VS Code 기반 IDE이고, Claude Code는 터미널 CLI 도구입니다. Cursor는 코드 편집에 특화되어 있고, Claude Code는 파일 시스템 조작, Git, 터미널 명령 실행 등 에이전트 방식으로 더 넓은 범위의 작업을 수행합니다."
      }
    },
    {
      "@type": "Question",
      "name": "Claude Code에서 MCP 서버는 어떻게 추가하나요?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "claude mcp add 서버이름 -- 실행명령 형식으로 추가합니다. 예를 들어 Python MCP 서버라면 claude mcp add my-server -- python server.py로 등록할 수 있습니다."
      }
    }
  ]
}
</script>

<h3>Claude Code는 무료인가요?</h3>
<p>Claude Code 자체는 무료로 설치할 수 있지만, API 사용량에 따라 비용이 발생합니다. Claude Pro나 Max 구독이 있으면 포함된 크레딧으로 사용할 수 있습니다.</p>

<h3>Claude Code와 Cursor의 차이점은?</h3>
<p>Cursor는 VS Code 기반 IDE이고, Claude Code는 터미널 CLI 도구입니다. Cursor는 코드 편집에 특화되어 있고, Claude Code는 파일 시스템 조작, Git, 터미널 명령 실행 등 에이전트 방식으로 더 넓은 범위의 작업을 수행합니다.</p>

<h3>Claude Code에서 MCP 서버는 어떻게 추가하나요?</h3>
<p><code>claude mcp add 서버이름 -- 실행명령</code> 형식으로 추가합니다. 예를 들어 Python MCP 서버라면 <code>claude mcp add my-server -- python server.py</code>로 등록할 수 있습니다.</p>

<p style="background-color: #f0f7ff; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0;">
관련 글: <a href="https://pearsoninsight.com/claude-code-install-guide-%ed%81%b4%eb%a1%9c%eb%93%9c_%ec%bd%94%eb%93%9c_%ec%84%a4%ec%b9%98/">클로드 코드 설치 가이드 — 터미널에서 AI 코딩하는 법 완전 정리 (2026)</a>
</p>
"""

# ── SEO 체크 ──────────────────────────────────────────────
print("=" * 60)
print("  STEP 1: SEO 체크")
print("=" * 60)
seo_result = wp_seo_check(CONTENT, FOCUS_KEYWORD, SEO_TITLE, META_DESCRIPTION, SLUG)
print(seo_result)

# ── 글 생성 (draft) ──────────────────────────────────────
print()
print("=" * 60)
print("  STEP 2: Draft 생성")
print("=" * 60)
create_result = wp_create_post(
    title=SEO_TITLE,
    content=CONTENT,
    focus_keyword=FOCUS_KEYWORD,
    seo_title=SEO_TITLE,
    meta_description=META_DESCRIPTION,
    slug=SLUG,
    excerpt=EXCERPT,
    category=CATEGORY,
    tags=TAGS,
    status="draft",
)
print(create_result)

# ID 추출
import re
id_match = re.search(r"ID: (\d+)", create_result)
if id_match:
    post_id = int(id_match.group(1))

    # ── 리뷰 ─────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  STEP 3: 리뷰 리포트")
    print("=" * 60)
    review = wp_review_draft(post_id)
    print(review)
