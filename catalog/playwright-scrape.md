# PLAYWRIGHT-SCRAPE - Playwright Stealth 크롤링

> headless 브라우저로 JS 렌더링 페이지를 크롤링할 때 사용.
> SPA, iframe, 봇 탐지 우회가 필요한 경우.
> 의존: 없음 (pip install playwright && playwright install chromium)

## 설치

```bash
pip install playwright
playwright install chromium
```

## 핵심 코드: Stealth 브라우저

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ],
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
    # webdriver 속성 숨기기 (봇 탐지 우회)
    await context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
    )
```

## 패턴: SPA 렌더링 대기 (폴링)

JS 프레임워크(Vue, React 등)로 렌더링되는 페이지는 `wait_for_selector` 대신
innerHTML 크기로 렌더링 완료를 판단:

```python
rendered = False
for _ in range(10):
    await page.wait_for_timeout(1500)
    length = await page.evaluate(
        "document.getElementById('app')?.innerHTML.length || 0"
    )
    if length > 1000:
        rendered = True
        break
```

## 패턴: iframe 내부 접근

```python
# iframe 이름으로 접근
frame = page.frame("iframe_name")
if frame:
    # iframe 내부에서 JS 실행
    data = await frame.evaluate("document.querySelector('.target').textContent")
```

## 패턴: 스크롤 + 지연 로딩

```python
# 스크롤하여 lazy-load 콘텐츠 로드
for _ in range(3):
    await page.mouse.wheel(0, 1500)
    await page.wait_for_timeout(800)
```

## 패턴: 랜덤 딜레이 (탐지 회피)

```python
import random, asyncio

delay = random.uniform(2.0, 5.0)
await asyncio.sleep(delay)
```

## 패턴: JS evaluate로 데이터 추출

```python
# 브라우저 컨텍스트에서 직접 DOM 쿼리
results = await page.evaluate(r"""() => {
    const items = [];
    document.querySelectorAll('.item').forEach(el => {
        items.push({
            title: el.querySelector('.title')?.textContent.trim(),
            url: el.querySelector('a')?.href,
        });
    });
    return items;
}""")
```

## 주의사항

- **Windows uvicorn**: Playwright는 `SelectorEventLoop`에서 동작 불가
  → `subprocess.run()` + `asyncio.to_thread()`로 별도 프로세스 실행
- **메모리**: headless Chromium은 200MB+ 사용, 동시 실행 주의
- **타임아웃**: 여러 페이지 순차 접속 시 전체 타임아웃 충분히 설정 (180초+)
- **User-Agent**: 실제 브라우저 UA 사용, 주기적 업데이트
- **headless 탐지**: `webdriver` 속성 + `AutomationControlled` 플래그 모두 처리

## 사용 예시 (네이버 검색 크롤링)

```python
from urllib.parse import quote

search_url = f"https://search.naver.com/search.naver?query={quote(keyword)}"

page = await context.new_page()
await page.goto(search_url, wait_until="domcontentloaded")
await page.wait_for_timeout(4000)

# 스크롤하여 추가 결과 로드
for _ in range(3):
    await page.mouse.wheel(0, 1500)
    await page.wait_for_timeout(800)

# 검색 결과 추출
results = await page.evaluate(r"""() => {
    const results = [];
    document.querySelectorAll('a[href*="cafe.naver.com/"]').forEach(a => {
        results.push({ title: a.textContent.trim(), url: a.href });
    });
    return results;
}""")
```
