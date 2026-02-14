# React + Vite + Tailwind v4

> 모던 프론트엔드 앱 시작 템플릿.
> Rackops 프로젝트에서 사용한 스택.

## 기술스택

| 항목 | 선택 | 버전 |
|------|------|------|
| Framework | React | 19 |
| Bundler | Vite | 6+ |
| CSS | Tailwind CSS | v4 |
| Language | TypeScript | 5+ |
| i18n | React Context | - |
| Font | 시스템 폰트 | 네트워크 불필요 |

## 프로젝트 생성

```bash
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install
npm install tailwindcss @tailwindcss/vite
```

## Tailwind v4 설정

### vite.config.ts
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

### src/index.css
```css
@import "tailwindcss";

@theme {
  --color-primary: #3b82f6;
  --color-surface: #1e293b;
  --color-background: #0f172a;
}
```

> **tailwind.config.js 필요 없음!** v4는 CSS 안에서 `@theme`으로 설정.

## 핵심 패턴

### 시스템 폰트 (에어갭 환경용)
```css
@theme {
  --font-sans: 'Segoe UI', -apple-system, 'Malgun Gothic', sans-serif;
}
```

### 다크테마 기본 레이아웃
```tsx
function App() {
  return (
    <div className="min-h-screen bg-background text-white">
      <header className="bg-surface border-b border-white/10 p-4">
        <h1 className="text-xl font-bold">Dashboard</h1>
      </header>
      <main className="max-w-7xl mx-auto p-6">
        {/* content */}
      </main>
    </div>
  )
}
```

### i18n (React Context)
```tsx
const translations = {
  ko: { title: '대시보드', save: '저장' },
  en: { title: 'Dashboard', save: 'Save' },
}

const I18nContext = createContext(translations.ko);

function App() {
  const [lang, setLang] = useState<'ko'|'en'>('ko');
  return (
    <I18nContext.Provider value={translations[lang]}>
      {/* children */}
    </I18nContext.Provider>
  );
}

// 사용
const t = useContext(I18nContext);
<h1>{t.title}</h1>
```

## AI 프롬프트 예시

```
React 19 + Vite + Tailwind v4로 대시보드를 만들어줘.
- 다크테마 기본
- 시스템 폰트 사용 (Google Fonts 금지)
- 한국어/영어 i18n 지원
- 위 레시피를 참고해서 구현해줘
```
