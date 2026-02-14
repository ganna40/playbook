# Tailwind CSS v4 삽질 방지

## 1. CSS 리셋 충돌

**증상**: `px-6`, `py-4`, `p-5` 같은 패딩/마진 클래스가 안 먹힘

**원인**: CSS에 `* { margin: 0; padding: 0; }` 를 직접 넣으면 Tailwind 유틸리티보다 specificity가 높아서 덮어씀

**해결**: 절대로 전역 리셋 넣지 말 것. Tailwind v4의 `@import "tailwindcss"`가 preflight(리셋)을 이미 포함하고 있음

```css
/* 절대 하지 마 */
* { margin: 0; padding: 0; }

/* 이것만 하면 됨 */
@import "tailwindcss";
```

## 2. 설정 방식 변경

**v3**: `tailwind.config.js` 파일에서 설정
**v4**: CSS 안 `@theme` 블록에서 설정

```css
/* v4 방식 */
@import "tailwindcss";

@theme {
  --color-primary: #3b82f6;
  --color-surface: #1e293b;
  --font-sans: 'Segoe UI', sans-serif;
}
```

사용: `bg-primary`, `text-surface`, `font-sans`

## 3. Vite 플러그인

v4는 PostCSS 대신 전용 Vite 플러그인 사용:

```bash
npm install tailwindcss @tailwindcss/vite
```

```typescript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'
export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

`postcss.config.js` 필요 없음.
