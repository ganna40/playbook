# [SWIPE] 스와이프 제스처

> 틴더식 카드 스와이프로 답변 입력.
> Touch Events + Mouse Events. 외부 라이브러리 불필요.

## 핵심 원리

1. `touchstart` / `mousedown` → 시작 X좌표 기록
2. `touchmove` / `mousemove` → deltaX 계산 → 카드 이동+회전
3. `touchend` / `mouseup` → 임계값(100px) 초과 시 답변 확정, 미만 시 복귀

## HTML

```html
<div class="swipe-zone" style="touch-action:none">
  <div class="swipe-card" id="swipeCard" style="background:linear-gradient(135deg,#ec4899,#8b5cf6)">
    <div class="swipe-stamp nope" id="stampNope">NOPE</div>
    <div class="swipe-stamp like" id="stampLike">LIKE</div>
    <div class="swipe-emoji">🎁</div>
    <div class="swipe-text">질문 텍스트</div>
    <div class="swipe-hint">← 비동의 | 동의 →</div>
  </div>
</div>
```

## CSS

```css
.swipe-zone { position:relative; height:340px; touch-action:none; user-select:none; }
.swipe-card {
  position:absolute; width:100%; height:100%; border-radius:24px;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  cursor:grab; padding:24px;
}
.swipe-stamp {
  position:absolute; top:24px; font-size:32px; font-weight:900;
  padding:8px 20px; border-radius:12px; border:4px solid;
  opacity:0; pointer-events:none;
}
.swipe-stamp.nope { left:16px; color:#ef4444; border-color:#ef4444; transform:rotate(-12deg); }
.swipe-stamp.like { right:16px; color:#22c55e; border-color:#22c55e; transform:rotate(12deg); }
```

## JS — 핵심 로직

```javascript
function initSwipe() {
  const card = document.getElementById('swipeCard');
  let startX = 0, curX = 0, dragging = false;

  function onStart(x) { startX = x; curX = 0; dragging = true; card.style.transition = 'none'; }

  function onMove(x) {
    if (!dragging) return;
    curX = x - startX;
    card.style.transform = `translateX(${curX}px) rotate(${curX * 0.08}deg)`;
    // NOPE/LIKE 라벨 페이드
    document.getElementById('stampNope').style.opacity = Math.min(1, Math.max(0, -curX / 100));
    document.getElementById('stampLike').style.opacity = Math.min(1, Math.max(0, curX / 100));
  }

  function onEnd() {
    if (!dragging) return;
    dragging = false;
    if (Math.abs(curX) > 100) {
      // 스와이프 확정: 날아가는 애니메이션
      const dir = curX > 0 ? 'right' : 'left';
      card.style.transition = 'transform .35s ease, opacity .35s ease';
      card.style.transform = `translateX(${curX > 0 ? 600 : -600}px) rotate(${curX > 0 ? 30 : -30}deg)`;
      card.style.opacity = '0';
      setTimeout(() => handleSwipe(dir), 350);
    } else {
      // 복귀
      card.style.transition = 'transform .3s ease';
      card.style.transform = 'none';
    }
  }

  // Touch
  card.addEventListener('touchstart', e => { e.preventDefault(); onStart(e.touches[0].clientX); }, { passive: false });
  card.addEventListener('touchmove',  e => { e.preventDefault(); onMove(e.touches[0].clientX); }, { passive: false });
  card.addEventListener('touchend', onEnd);

  // Mouse (데스크탑)
  card.addEventListener('mousedown', e => onStart(e.clientX));
  document.addEventListener('mousemove', e => { if (dragging) onMove(e.clientX); });
  document.addEventListener('mouseup', () => { if (dragging) onEnd(); });
}
```

## 주요 파라미터

| 값 | 기본 | 설명 |
|----|------|------|
| 임계값 | 100px | 스와이프 확정 최소 이동 |
| 회전 계수 | 0.08 | deltaX × 0.08 = 회전각(deg) |
| 날아감 거리 | 600px | 확정 시 카드 이탈 거리 |
| 전환 시간 | 350ms | 날아가는 애니메이션 |

## 삽질 방지

- `touch-action: none` 필수 — 없으면 브라우저 기본 스크롤과 충돌
- `passive: false` 필수 — `e.preventDefault()` 안 먹힘
- 마우스 이벤트는 `document`에 바인딩 — 카드 밖으로 나가도 추적
