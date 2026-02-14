# [STYLE-DARK] 다크 테마

> pong, amlife 스타일. 어두운 배경 + 보라/빨강 악센트.

## CSS Variables

```css
:root {
  --bg: #0a0a0f;
  --card: #14141f;
  --card2: #1a1a2e;
  --border: #2a2a3e;
  --t1: #ffffff;
  --t2: #a0a0b8;
  --t3: #6b6b80;
  --accent: #7c3aed;
  --accent2: #a855f7;
  --danger: #ef4444;
  --warn: #f59e0b;
  --safe: #22c55e;
}

body {
  background: var(--bg);
  color: var(--t1);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
               'Noto Sans KR', sans-serif;
}
```

## 카드 스타일

```css
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 24px;
}
```

## 버튼 스타일

```css
.btn-primary {
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: #fff;
  border: none;
  border-radius: 14px;
  padding: 16px;
  font-size: 16px;
  font-weight: 700;
  width: 100%;
  cursor: pointer;
  transition: transform 0.1s, opacity 0.2s;
}
.btn-primary:active { transform: scale(0.97) }

/* O/X 버튼 */
.btn-yes {
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: #22c55e;
}
.btn-no {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
}
```
