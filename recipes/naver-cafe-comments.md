# 네이버 카페 댓글 크롤링 (로그인 없이)

> Playwright로 네이버 카페 글의 실제 댓글을 추출하는 기법.
> 핵심: 검색 결과의 `?art=` JWT 토큰 → iframe 내 Vue SPA 렌더링 대기 → 댓글 셀렉터

## 왜 어려운가

1. 네이버 카페 글은 **로그인 필수** (비회원 접근 차단)
2. 글 본문/댓글이 **iframe (`#cafe_main`) 안의 Vue SPA**로 렌더링
3. Vue SPA는 JS 실행 후에야 DOM 생성 (SSR 아님)
4. 일반 크롤러(requests, BeautifulSoup)로는 접근 불가

## 핵심 발견: `?art=` JWT 토큰

네이버 **검색 결과**에 표시되는 카페 글 링크에는 `?art=` 파라미터가 붙는다:
```
https://cafe.naver.com/cafename/12345?art=aWQ9....(JWT)
```

이 토큰은 **로그인 없이 해당 글에 접근할 수 있는 일시적 인증 토큰**이다.
검색 엔진 크롤러를 위해 네이버가 발급하는 것으로 추정.

## 전체 흐름

```
1. 네이버 통합검색 (search.naver.com?query=키워드)
   → Playwright로 접속, 스크롤하여 카페 영역 로드
   ↓
2. 카페 글 URL 추출 (a[href*="cafe.naver.com/"])
   → ?art= 토큰이 포함된 URL만 사용 가능
   ↓
3. ?art= URL로 카페 글 접속
   → 페이지 로드 후 5초 대기
   ↓
4. cafe_main iframe 접근
   → page.frame("cafe_main")
   ↓
5. Vue SPA 렌더링 대기 (폴링)
   → #app의 innerHTML.length > 1000 확인
   → 미렌더링 시 49자 ("JavaScript enabled" 에러)
   ↓
6. 스크롤 → 댓글 추출
   → .comment_text_box .text_comment
```

## 코드

### Playwright 브라우저 설정 (Stealth)

```python
browser = await p.chromium.launch(
    headless=True,
    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
)
context = await browser.new_context(
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    viewport={"width": 1280, "height": 900},
    locale="ko-KR",
)
await context.add_init_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
)
```

### 검색 결과에서 ?art= URL 추출

```javascript
// page.evaluate() 내부
const allLinks = document.querySelectorAll('a[href*="cafe.naver.com/"]');
for (const a of allLinks) {
    const href = a.href;
    const m = href.match(/cafe\.naver\.com\/([^/?#]+)\/(\d+)/);
    if (!m) continue;
    // ?art= 토큰이 있는 URL만 사용
    if (href.includes('?art=')) {
        results.push({ url: href, title: a.textContent.trim() });
    }
}
```

### iframe 접근 + Vue SPA 렌더링 대기

```python
# cafe_main iframe 접근
cafe_frame = page.frame("cafe_main")
if not cafe_frame:
    # iframe 없으면 스킵

# Vue SPA 렌더링 대기 (폴링)
rendered = False
for _ in range(10):
    await page.wait_for_timeout(1500)
    app_len = await cafe_frame.evaluate(
        "(() => { const a = document.getElementById('app'); "
        "return a ? a.innerHTML.length : 0; })()"
    )
    if app_len > 1000:  # 49자 = 미렌더링, 1000+ = 정상
        rendered = True
        break
```

### 댓글 추출

```python
# 스크롤하여 댓글 영역 로드
await cafe_frame.evaluate("window.scrollTo(0, document.body.scrollHeight)")
await page.wait_for_timeout(2000)

# 실제 댓글 텍스트 추출
comments = await cafe_frame.evaluate(r"""() => {
    const comments = [];
    const els = document.querySelectorAll('.comment_text_box .text_comment');
    els.forEach(el => {
        const text = el.textContent.trim();
        if (text && text.length > 1) comments.push(text);
    });
    return comments;
}""")
```

## Windows uvicorn 주의사항

uvicorn(Windows)의 `SelectorEventLoop`에서 Playwright subprocess 생성이 불가능하다:
```
NotImplementedError: Playwright requires ProactorEventLoop
```

**해결**: 별도 Python 프로세스로 실행

```python
# comment_checker.py
import subprocess, asyncio

async def verify_keyword(keyword, brand_name):
    def _run():
        result = subprocess.run(
            [sys.executable, "_comment_worker.py", keyword, brand_name],
            capture_output=True, text=True, timeout=180, encoding="utf-8",
        )
        return json.loads(result.stdout)
    return await asyncio.to_thread(_run)
```

## 주의사항

- `?art=` 토큰은 **검색 결과에서만** 발급됨 (직접 URL 조합 불가)
- 토큰은 일시적이며 만료될 수 있음
- Vue SPA 렌더링에 최대 15초+ 걸릴 수 있음
- 게시글 간 **랜덤 딜레이(2~5초)** 필수 (IP 차단 방지)
- headless 탐지 우회: `webdriver` 속성 숨기기 + `AutomationControlled` 비활성화
- 네이버 카페 구조 변경 시 셀렉터 업데이트 필요 (`.comment_text_box .text_comment`)
