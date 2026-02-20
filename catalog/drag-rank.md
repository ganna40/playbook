# [DRAG-RANK] 드래그 순위 매기기

> 항목을 터치/마우스로 드래그해서 우선순위를 정하는 모듈.
> 순위별 가중치 곱셈으로 점수 계산.

## HTML

```html
<div class="rank-list" id="rankList">
  <div class="rank-item" data-idx="0">
    <span class="rank-handle">☰</span>
    <span class="rank-emoji">😂</span>
    <span class="rank-text">유머/재치</span>
    <span class="rank-num">1</span>
  </div>
  <div class="rank-item" data-idx="1">
    <span class="rank-handle">☰</span>
    <span class="rank-emoji">💕</span>
    <span class="rank-text">따뜻한 배려</span>
    <span class="rank-num">2</span>
  </div>
  <!-- ... -->
</div>
<button class="btn-confirm" onclick="pickRank()">확인</button>
```

## CSS

```css
.rank-item {
  display: flex; align-items: center; gap: 12px;
  background: var(--card); border: 2px solid var(--border);
  border-radius: 14px; padding: 14px 16px;
  cursor: grab; touch-action: none; user-select: none;
  transition: transform .15s, box-shadow .15s;
}
.rank-item.dragging {
  z-index: 10;
  box-shadow: 0 8px 32px rgba(168,85,247,.4);
  border-color: var(--purple2);
  transform: scale(1.03);
}
```

## JS — 핵심 로직

```javascript
function initRank() {
  const list = document.getElementById('rankList');
  let dragEl = null, startY = 0, offsetY = 0;
  const ITEM_H = 60; // 아이템 높이 + 갭

  function onStart(el, y) {
    dragEl = el;
    startY = y;
    offsetY = 0;
    el.classList.add('dragging');
  }

  function onMove(y) {
    if (!dragEl) return;
    offsetY = y - startY;
    dragEl.style.transform = `translateY(${offsetY}px)`;

    const items = Array.from(list.querySelectorAll('.rank-item'));
    const curIdx = items.indexOf(dragEl);

    // 아래로 스왑
    if (offsetY > ITEM_H / 2 && curIdx < items.length - 1) {
      list.insertBefore(items[curIdx + 1], dragEl);
      startY += ITEM_H;
      offsetY -= ITEM_H;
      dragEl.style.transform = `translateY(${offsetY}px)`;
      updateNums();
    }
    // 위로 스왑
    else if (offsetY < -ITEM_H / 2 && curIdx > 0) {
      list.insertBefore(dragEl, items[curIdx - 1]);
      startY -= ITEM_H;
      offsetY += ITEM_H;
      dragEl.style.transform = `translateY(${offsetY}px)`;
      updateNums();
    }
  }

  function onEnd() {
    if (!dragEl) return;
    dragEl.classList.remove('dragging');
    dragEl.style.transform = 'none';
    dragEl = null;
  }

  function updateNums() {
    list.querySelectorAll('.rank-item').forEach((it, i) =>
      it.querySelector('.rank-num').textContent = i + 1
    );
  }

  // Touch
  list.addEventListener('touchstart', e => {
    const item = e.target.closest('.rank-item');
    if (item) { e.preventDefault(); onStart(item, e.touches[0].clientY); }
  }, { passive: false });
  list.addEventListener('touchmove', e => {
    if (dragEl) { e.preventDefault(); onMove(e.touches[0].clientY); }
  }, { passive: false });
  list.addEventListener('touchend', onEnd);

  // Mouse
  list.addEventListener('mousedown', e => {
    const item = e.target.closest('.rank-item');
    if (item) onStart(item, e.clientY);
  });
  document.addEventListener('mousemove', e => { if (dragEl) onMove(e.clientY); });
  document.addEventListener('mouseup', onEnd);
}
```

## 점수 계산 — 가중치 곱셈

```javascript
function pickRank() {
  const items = document.querySelectorAll('#rankList .rank-item');
  const order = Array.from(items).map(it => parseInt(it.dataset.idx));
  const multipliers = [4, 3, 2, 1]; // 1위=×4, 2위=×3 ...

  order.forEach((origIdx, rank) => {
    const scores = Q[idx].items[origIdx].scores;
    for (const [ax, v] of Object.entries(scores)) {
      axisScore[ax] += v * multipliers[rank];
    }
  });
}
```

## 질문 데이터 구조

```javascript
{
  type: 'rank',
  cat: '가치관',
  text: '중요한 순서대로 정렬하세요',
  items: [
    { text: '유머/재치',   emoji: '😂', scores: { adv: 1 } },
    { text: '따뜻한 배려', emoji: '💕', scores: { rom: 1, emo: 1 } },
    { text: '경제적 안정', emoji: '💰', scores: { stb: 1 } },
    { text: '지적 대화',   emoji: '🧠', scores: { ind: 1 } },
  ]
}
```

## URL 인코딩

순서를 인덱스 문자열로:

```javascript
answers.push(order.join('')); // "2031" = 아이템2가 1위, 아이템0이 2위 ...
```

## 삽질 방지

- **`touch-action: none`** — 모바일 스크롤 방지
- **`passive: false`** — `preventDefault()` 필수
- **ITEM_H 값** — CSS의 실제 아이템 높이+갭과 일치해야 함
- **DOM 직접 조작** — `insertBefore`로 실제 DOM 순서 변경
- **4개 항목이 적정** — 5개 이상은 모바일에서 불편
