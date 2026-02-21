# [VIEW-TRANSITIONS] 화면 전환 — View Transitions API

> 입력 → 결과 화면 전환 시 네이티브 앱 같은 애니메이션.
> `document.startViewTransition()`으로 DOM 변경을 감싸면 자동 전환 효과.

## 핵심 로직

```javascript
function showResults() {
  const inputPanel = document.getElementById('inputPanel');
  const resultPanel = document.getElementById('resultPanel');

  function doTransition() {
    inputPanel.style.display = 'none';
    resultPanel.style.display = 'block';
  }

  // View Transitions API 지원 시 애니메이션, 미지원 시 즉시 전환
  if (document.startViewTransition) {
    document.startViewTransition(doTransition);
  } else {
    doTransition();
  }
}
```

## CSS (커스텀 전환 애니메이션)

```css
/* 결과 패널에 view-transition-name 지정 */
#resultPanel {
  view-transition-name: results-panel;
}
#inputPanel {
  view-transition-name: input-panel;
}

/* 결과 패널: 아래에서 올라오며 페이드인 */
::view-transition-old(results-panel) {
  animation: fadeSlideOut 0.3s ease-in forwards;
}
::view-transition-new(results-panel) {
  animation: fadeSlideIn 0.4s ease-out forwards;
}

/* 입력 패널: 위로 올라가며 페이드아웃 */
::view-transition-old(input-panel) {
  animation: fadeSlideUp 0.3s ease-in forwards;
}
::view-transition-new(input-panel) {
  animation: fadeSlideDown 0.4s ease-out forwards;
}

@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(30px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeSlideOut {
  from { opacity: 1; transform: translateY(0); }
  to   { opacity: 0; transform: translateY(-20px); }
}
@keyframes fadeSlideUp {
  from { opacity: 1; transform: translateY(0); }
  to   { opacity: 0; transform: translateY(-30px); }
}
@keyframes fadeSlideDown {
  from { opacity: 0; transform: translateY(30px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

## 삽질 방지

- **반드시 graceful degradation** — `if (document.startViewTransition)` 체크. 미지원 브라우저에서 그냥 DOM 변경
- **`view-transition-name`은 고유해야 함** — 같은 이름이 여러 요소에 있으면 충돌
- **콜백 안에서 DOM 변경** — `startViewTransition(callback)` 콜백 안에서 실제 display 변경
- **Chrome 111+ / Safari 18+ 지원** — Firefox는 아직 미지원 (2026 기준)
- **html2canvas와 충돌 없음** — View Transitions는 CSS 레이어라 캡처에 영향 안 줌
