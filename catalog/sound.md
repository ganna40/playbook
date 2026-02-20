# [SOUND] 효과음 — Web Audio API

> OscillatorNode로 효과음 생성. 외부 오디오 파일 불필요.
> 단일 HTML 파일에서 사운드 피드백 구현.

## 핵심 로직

```javascript
const SFX = {
  ctx: null,
  muted: false,

  init() {
    try { this.ctx = new (window.AudioContext || window.webkitAudioContext)(); }
    catch(e) {}
  },

  _play(freq, dur, type, vol) {
    if (this.muted || !this.ctx) return;
    if (this.ctx.state === 'suspended') this.ctx.resume();

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.connect(gain);
    gain.connect(this.ctx.destination);

    osc.type = type || 'sine';        // sine, triangle, square, sawtooth
    osc.frequency.value = freq;       // Hz
    gain.gain.setValueAtTime(vol || 0.15, this.ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + dur);

    osc.start();
    osc.stop(this.ctx.currentTime + dur);
  },

  // 프리셋
  tick()    { this._play(660, 0.06, 'sine', 0.12); },
  swipeR()  { this._play(520, 0.15); setTimeout(() => this._play(780, 0.12), 80); },
  swipeL()  { this._play(400, 0.15, 'triangle'); setTimeout(() => this._play(300, 0.12, 'triangle'), 80); },
  slide()   { this._play(440, 0.04, 'sine', 0.08); },
  rank()    { this._play(550, 0.08); },
  reveal()  {
    [523, 659, 784, 1047].forEach((f, i) =>
      setTimeout(() => this._play(f, 0.25, 'sine', 0.12), i * 120)
    );
  },
};
```

## 음소거 버튼

```html
<button class="mute-btn" onclick="toggleMute()">🔊</button>
```

```javascript
function toggleMute() {
  SFX.muted = !SFX.muted;
  document.querySelector('.mute-btn').textContent = SFX.muted ? '🔇' : '🔊';
}
```

## 효과음 프리셋 가이드

| 이름 | 주파수(Hz) | 길이(s) | 파형 | 용도 |
|------|-----------|---------|------|------|
| tick | 660 | 0.06 | sine | 버튼 클릭 |
| swipeR | 520→780 | 0.15 | sine | 오른쪽 스와이프 (상승) |
| swipeL | 400→300 | 0.15 | triangle | 왼쪽 스와이프 (하강) |
| slide | 440 | 0.04 | sine | 슬라이더 이동 |
| rank | 550 | 0.08 | sine | 순위 이동 |
| reveal | 523→659→784→1047 | 0.25×4 | sine | 결과 공개 (도미솔도 아르페지오) |

## 삽질 방지

- **`SFX.init()`은 사용자 인터랙션 안에서 호출** — 자동재생 정책 때문
- **`ctx.resume()`** — 모바일에서 AudioContext가 suspended 상태일 수 있음
- **볼륨은 0.08~0.15** — 너무 크면 불쾌, 너무 작으면 안 들림
- **음소거 기본 제공** — 사용자가 끌 수 있어야 함
