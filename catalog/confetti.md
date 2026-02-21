# [CONFETTI] 축하 효과 — canvas-confetti

> 결과 공개, 등급 확인 등에 축하 컨페티 효과.
> 가벼운 라이브러리 (7KB gzipped). Canvas 기반.

## CDN

```html
<script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>
```

## 핵심 로직

```javascript
// 기본 발사
confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });

// 3방향 동시 발사 (화려한 연출)
function celebrationConfetti() {
  confetti({ particleCount: 60, angle: 60, spread: 55, origin: { x: 0 } });
  confetti({ particleCount: 60, angle: 90, spread: 70, origin: { y: 0.6 } });
  confetti({ particleCount: 60, angle: 120, spread: 55, origin: { x: 1 } });
}

// 등급별 차등 발사
function gradeConfetti(grade) {
  const configs = {
    S: { particleCount: 150, spread: 100, colors: ['#FFD700', '#FFA500'] },
    A: { particleCount: 100, spread: 80, colors: ['#00D4AA', '#00B4D8'] },
    B: { particleCount: 60, spread: 60 },
    C: { particleCount: 30, spread: 40 }
  };
  const cfg = configs[grade] || configs.C;
  confetti({
    ...cfg,
    origin: { y: 0.6 },
    ticks: 200,
    gravity: 1.2
  });
}
```

## 주요 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `particleCount` | 50 | 파티클 수 |
| `spread` | 45 | 발사 각도 범위 (도) |
| `origin` | `{x:0.5, y:0.5}` | 발사 위치 (0~1) |
| `angle` | 90 | 발사 방향 (도) |
| `colors` | 랜덤 | 색상 배열 |
| `ticks` | 200 | 파티클 수명 |
| `gravity` | 1 | 중력 강도 |
| `scalar` | 1 | 파티클 크기 배율 |

## 삽질 방지

- **모바일 성능** — `particleCount`를 150 이하로 유지. 저사양 기기에서 프레임 드롭
- **타이밍** — 결과 텍스트가 보인 후 살짝 딜레이(200~300ms) 후 발사가 자연스러움
- **반복 발사 금지** — setInterval로 반복하면 캔버스 누적. 1회 또는 2~3회만
- **배경 투명** — confetti 캔버스가 `position: fixed`로 전체 화면 덮음. 클릭 이벤트는 통과함
