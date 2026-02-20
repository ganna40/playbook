# [SPECTRUM] 슬라이더 답변

> `<input type="range">`로 0~100 연속 스펙트럼 답변.
> 양 끝에 이모지+라벨, 실시간 값 표시.

## HTML

```html
<div class="spectrum-zone">
  <div class="q-text">연인과의 연락 빈도는?</div>
  <div class="spec-row">
    <div class="spec-end">
      <div class="spec-end-emoji">🕊️</div>
      <div class="spec-end-text">자유롭게</div>
    </div>
    <input type="range" min="0" max="100" value="50" class="spec-slider" id="specSlider">
    <div class="spec-end">
      <div class="spec-end-emoji">📱</div>
      <div class="spec-end-text">수시로</div>
    </div>
  </div>
  <div class="spec-value" id="specValue">50</div>
  <button class="btn-confirm" onclick="pickSpectrum()">확인</button>
</div>
```

## CSS — 커스텀 슬라이더

```css
.spec-slider {
  -webkit-appearance: none;
  flex: 1; height: 8px;
  background: var(--card2);
  border-radius: 4px; outline: none;
}
.spec-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, var(--pink), var(--purple));
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(168,85,247,.5);
  border: 3px solid #fff;
}
```

## JS — 점수 보간

```javascript
function pickSpectrum() {
  const val = parseInt(document.getElementById('specSlider').value);
  const q = Q[idx];
  const t = val / 100; // 0=left, 1=right

  // 양쪽 점수를 보간
  const allAxes = new Set([
    ...Object.keys(q.leftScores),
    ...Object.keys(q.rightScores)
  ]);

  for (const ax of allAxes) {
    const lv = q.leftScores[ax] || 0;
    const rv = q.rightScores[ax] || 0;
    const score = Math.round(lv * (1 - t) + rv * t);
    axisScore[ax] += score;
  }
}
```

## 질문 데이터 구조

```javascript
{
  type: 'spectrum',
  cat: '소통',
  text: '연인과의 연락 빈도는?',
  leftLabel: '자유롭게',
  rightLabel: '수시로',
  leftEmoji: '🕊️',
  rightEmoji: '📱',
  leftScores: { ind: 2 },        // 0에 가까울 때
  rightScores: { rom: 2, emo: 1 } // 100에 가까울 때
}
```

## URL 인코딩

슬라이더 값 0~100을 한 자리(0~9)로 압축:

```javascript
answers.push(String(Math.round(val / 11.2))); // 0~100 → 0~9
```

복원:

```javascript
const val = parseInt(encoded) * 11.2; // 0~9 → 약 0~100
```

## 삽질 방지

- **기본값 50** — 중립 위치에서 시작
- **실시간 값 표시** — `input` 이벤트로 숫자 업데이트
- **moz 스타일도 작성** — Firefox는 `::-moz-range-thumb` 사용
- **확인 버튼 필수** — 슬라이더만으로는 답변 확정 시점이 불분명
