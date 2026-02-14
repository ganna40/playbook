# [STYLE-LIGHT] 라이트 테마

> salary, mz 스타일. 밝은 배경 + 파란 악센트.

## CSS Variables

```css
:root {
  --bg: #f4f5f7;
  --card: #ffffff;
  --card2: #f8f9fb;
  --border: #eceef1;
  --t1: #191f28;
  --t2: #4e5968;
  --t3: #8b95a1;
  --t4: #b0b8c1;
  --accent: #3182f6;
  --accent-light: rgba(49, 130, 246, 0.06);
  --accent-mid: rgba(49, 130, 246, 0.12);
  --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 2px 12px rgba(0,0,0,0.04);
  --shadow-lg: 0 4px 24px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04);
  --radius: 16px;
}

body {
  background: var(--bg);
  color: var(--t1);
  font-family: 'Pretendard Variable', Pretendard, -apple-system,
               BlinkMacSystemFont, system-ui, sans-serif;
}
```

## Pretendard 폰트 로드

```html
<link rel="stylesheet" as="style" crossorigin
  href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css" />
```

## 카드 스타일

```css
.card {
  background: var(--card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 24px;
}
```

## 버튼 스타일

```css
.btn-primary {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 14px;
  padding: 16px;
  font-size: 16px;
  font-weight: 700;
  width: 100%;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(49, 130, 246, 0.3);
  transition: transform 0.1s;
}
.btn-primary:active { transform: scale(0.97) }

/* 선택지 버튼 */
.btn-option {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  text-align: left;
  width: 100%;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-option:hover {
  border-color: var(--accent);
  background: var(--accent-light);
}
```

## Tailwind CDN 사용 시

```html
<script src="https://cdn.tailwindcss.com"></script>
```

salary에서는 Tailwind CDN으로 유틸리티 클래스 사용.
나머지(pong, mz, amlife)는 순수 CSS.
