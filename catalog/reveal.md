# [REVEAL] 결과 공개 연출

> 퀴즈 완료 후 등급 공개 전 드라마틱 연출.
> 몰입감 + 공유 욕구 극대화.

## 패턴: 분석 중 → 오버레이 → 등급 공개

```javascript
function showAnalyzing() {
  showScreen('analyzing');
  // 2초 후 드라마틱 공개
  setTimeout(() => dramaticReveal(), 2000);
}

function dramaticReveal() {
  const overlay = document.getElementById('reveal-overlay');
  overlay.classList.add('active');

  // 1단계: 흔들림
  overlay.innerHTML = '<div class="reveal-shake">분석 완료</div>';

  setTimeout(() => {
    // 2단계: 등급 슬램
    const grade = calculateGrade();
    overlay.innerHTML = `
      <div class="reveal-grade ${grade.cls}">
        <span class="reveal-emoji">${grade.emoji}</span>
        <span class="reveal-name">${grade.name}</span>
      </div>
    `;
    spawnConfetti(grade.colors);
  }, 800);

  setTimeout(() => {
    overlay.classList.remove('active');
    showScreen('result');
  }, 2500);
}
```

## 등급별 연출 (pong 스타일)

```javascript
// 좋은 등급 (시그마, 알파): 금빛 + 컨페티
if (grade.id === 'S' || grade.id === 'A') {
  el.style.animation = 'fadeScale 0.6s ease';
  spawnConfetti(['#ffd700', '#ffec44', '#fff']);
}

// 나쁜 등급 (델타, 오메가): 글리치 + 빨간 플래시
if (grade.id === 'D' || grade.id === 'F') {
  el.style.animation = 'glitchIn 0.8s ease';
  flashScreen('red');
}
```

## 핵심 애니메이션 CSS

```css
/* 등급 슬램 (위에서 쾅) */
@keyframes slamIn {
  0% { transform: scale(3); opacity: 0 }
  60% { transform: scale(0.9) }
  100% { transform: scale(1); opacity: 1 }
}

/* 글리치 (나쁜 등급) */
@keyframes glitchIn {
  0% { opacity: 0; transform: scale(3) skewX(20deg) }
  20% { opacity: 1; transform: scale(0.8) skewX(-10deg) }
  40% { transform: scale(1.1) skewX(5deg) }
  100% { transform: scale(1) skewX(0) }
}

/* 흔들림 */
@keyframes shakeHard {
  0%, 100% { transform: translateX(0) }
  25% { transform: translateX(-8px) rotate(-2deg) }
  75% { transform: translateX(8px) rotate(2deg) }
}

/* 도장 찍기 */
@keyframes stampSlam {
  0% { transform: rotate(-12deg) scale(4); opacity: 0 }
  60% { transform: rotate(-12deg) scale(0.9); opacity: 0.9 }
  100% { transform: rotate(-12deg) scale(1); opacity: 0.85 }
}

/* 빨간 플래시 */
@keyframes flashRed {
  0%, 100% { opacity: 0 }
  50% { opacity: 1; background: rgba(255,0,0,0.3) }
}
```

## 컨페티

```javascript
function spawnConfetti(colors) {
  for (let i = 0; i < 40; i++) {
    const el = document.createElement('div');
    el.className = 'confetti-piece';
    el.style.left = Math.random() * 100 + 'vw';
    el.style.background = colors[Math.floor(Math.random() * colors.length)];
    el.style.width = (6 + Math.random() * 8) + 'px';
    el.style.height = (6 + Math.random() * 8) + 'px';
    el.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
    el.style.animationDuration = (2 + Math.random() * 3) + 's';
    el.style.animationDelay = (Math.random() * 1.5) + 's';
    document.body.appendChild(el);
  }
}
```

```css
.confetti-piece {
  position: fixed;
  top: -10px;
  z-index: 9999;
  pointer-events: none;
  animation: confettiFall linear forwards;
}
@keyframes confettiFall {
  0% { transform: translateY(-100vh) rotate(0) }
  100% { transform: translateY(100vh) rotate(720deg) }
}
```
