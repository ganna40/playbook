# [TIMER] 질문 타이머

> 질문당 제한시간. 긴장감 + 직관적 답변 유도.
> pong, mz, amlife에서 사용 (15초).

## HTML

```html
<div class="timer-wrap">
  <div class="timer-bar" id="timerBar"></div>
</div>
<div class="timer-num" id="timerNum">15</div>
```

## JavaScript

```javascript
let TIMER_ID = null;
let TIMER_SEC = 15;

function startTimer() {
  clearInterval(TIMER_ID);
  TIMER_SEC = 15;

  const bar = document.getElementById('timerBar');
  const num = document.getElementById('timerNum');

  bar.style.transition = 'none';
  bar.style.width = '100%';
  bar.classList.remove('urgent');
  num.classList.remove('urgent');
  num.textContent = '15';

  void bar.offsetWidth; // force reflow

  bar.style.transition = 'width 1s linear';

  TIMER_ID = setInterval(() => {
    TIMER_SEC--;
    num.textContent = TIMER_SEC;
    bar.style.width = (TIMER_SEC / 15 * 100) + '%';

    if (TIMER_SEC <= 5) {
      bar.classList.add('urgent');
      num.classList.add('urgent');
    }

    if (TIMER_SEC <= 0) {
      clearInterval(TIMER_ID);
      autoAnswer(); // 시간 초과 시 기본값 선택
    }
  }, 1000);
}

function clearTimer() {
  clearInterval(TIMER_ID);
}
```

## CSS

```css
.timer-wrap {
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 100px;
  overflow: hidden;
  margin-bottom: 12px;
}
.timer-bar {
  height: 100%;
  background: var(--accent);
  border-radius: 100px;
}
.timer-bar.urgent { background: var(--danger) }
.timer-num { font-size: 14px; color: var(--t3); text-align: center }
.timer-num.urgent { color: var(--danger); font-weight: 700 }
```

## 주의사항

- `void bar.offsetWidth` 로 reflow 강제해야 transition 리셋됨
- 타이머 초과 시 자동 답변 처리 필수 (안 하면 멈춤)
- 화면 전환 시 `clearTimer()` 호출 필수
