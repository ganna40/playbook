# [RADAR] 레이더 차트

> Canvas로 다차원 점수를 시각화.
> mz, amlife에서 사용.

## 함수

```javascript
function drawRadarChart(canvasId, categories, scores, options = {}) {
  const canvas = document.getElementById(canvasId);
  const ctx = canvas.getContext('2d');
  const W = canvas.width = options.size || 300;
  const H = canvas.height = options.size || 300;
  const cx = W / 2, cy = H / 2;
  const R = Math.min(cx, cy) - 40;
  const n = categories.length;
  const accentColor = options.color || '#3182f6';

  ctx.clearRect(0, 0, W, H);

  // 각도 계산
  const angles = categories.map((_, i) => (Math.PI * 2 * i / n) - Math.PI / 2);

  // 배경 그리드 (5단계)
  for (let level = 1; level <= 5; level++) {
    const r = R * level / 5;
    ctx.beginPath();
    angles.forEach((a, i) => {
      const x = cx + r * Math.cos(a);
      const y = cy + r * Math.sin(a);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.strokeStyle = 'rgba(255,255,255,0.1)';
    ctx.stroke();
  }

  // 축 선
  angles.forEach(a => {
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + R * Math.cos(a), cy + R * Math.sin(a));
    ctx.strokeStyle = 'rgba(255,255,255,0.1)';
    ctx.stroke();
  });

  // 데이터 영역
  ctx.beginPath();
  angles.forEach((a, i) => {
    const val = (scores[i] || 0) / 100; // 0~100 → 0~1
    const x = cx + R * val * Math.cos(a);
    const y = cy + R * val * Math.sin(a);
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.closePath();
  ctx.fillStyle = accentColor + '33'; // 20% 투명
  ctx.fill();
  ctx.strokeStyle = accentColor;
  ctx.lineWidth = 2;
  ctx.stroke();

  // 데이터 포인트
  angles.forEach((a, i) => {
    const val = (scores[i] || 0) / 100;
    const x = cx + R * val * Math.cos(a);
    const y = cy + R * val * Math.sin(a);
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fillStyle = accentColor;
    ctx.fill();
  });

  // 라벨
  ctx.fillStyle = '#e2e8f0';
  ctx.font = '12px sans-serif';
  ctx.textAlign = 'center';
  angles.forEach((a, i) => {
    const labelR = R + 24;
    const x = cx + labelR * Math.cos(a);
    const y = cy + labelR * Math.sin(a) + 4;
    ctx.fillText(categories[i], x, y);
  });
}
```

## 사용

```html
<canvas id="radar-chart"></canvas>

<script>
drawRadarChart('radar-chart',
  ['성격', '소통', '경제', '감성', '자율', '건강', '디지털', '취미'],
  [85, 60, 70, 90, 45, 80, 95, 55],  // 각 카테고리 점수 (0~100)
  { size: 300, color: '#3182f6' }
);
</script>
```

## 주의사항

- Canvas는 `html2canvas`로 스크린샷 시 자동 포함됨
- `scores`는 0~100 범위로 정규화 필요
- 카테고리가 6~8개일 때 가장 보기 좋음
- 모바일에서는 `size: 280` 정도가 적당
