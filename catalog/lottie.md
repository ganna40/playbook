# [LOTTIE] 벡터 애니메이션 — lottie-web

> 디자이너가 만든 예쁜 애니메이션을 웹에서 그대로 재생해주는 기술.
> GIF와 비슷하지만, 파일이 훨씬 가볍고 아무리 확대해도 깨지지 않는다 (벡터 방식).
> JSON 파일 하나에 애니메이션 정보가 다 들어있어서, 코드로 속도/반복/색상도 바꿀 수 있다.

## CDN

```html
<script src="https://cdn.jsdelivr.net/npm/lottie-web@5.12.2/build/player/lottie.min.js"></script>
```

## 핵심 로직

```javascript
// JSON URL에서 로드
const anim = lottie.loadAnimation({
  container: document.getElementById('lottieContainer'),
  renderer: 'svg',          // 'svg' | 'canvas' | 'html'
  loop: false,               // 반복 재생
  autoplay: true,            // 자동 재생
  path: '/animation.json'    // Lottie JSON 경로
});

// 인라인 JSON 데이터로 로드 (외부 파일 불필요)
const anim2 = lottie.loadAnimation({
  container: document.getElementById('lottieContainer'),
  renderer: 'svg',
  loop: false,
  autoplay: false,
  animationData: LOTTIE_JSON  // JS 객체 직접 전달
});

// 제어
anim2.play();
anim2.stop();
anim2.goToAndPlay(0, true);   // 프레임 0부터 재생
anim2.setSpeed(1.5);          // 1.5배속
```

## 인라인 JSON 직접 작성 (간단한 애니메이션)

```javascript
const LOTTIE_CELEBRATION = {
  v: "5.7.4",
  fr: 30,               // 프레임레이트
  ip: 0,                // 시작 프레임
  op: 40,               // 끝 프레임
  w: 200, h: 200,       // 캔버스 크기
  layers: [
    {
      ty: 4,             // Shape Layer
      nm: "ring",
      ip: 0, op: 40,
      st: 0,
      ks: {              // Transform
        o: { a: 1, k: [  // 불투명도 키프레임
          { t: 0, s: [100] },
          { t: 30, s: [0] }
        ]},
        s: { a: 1, k: [  // 스케일 키프레임
          { t: 0, s: [30, 30, 100] },
          { t: 30, s: [120, 120, 100] }
        ]},
        p: { a: 0, k: [100, 100, 0] },  // 위치 (중앙)
        a: { a: 0, k: [0, 0, 0] },
        r: { a: 0, k: 0 }
      },
      shapes: [{
        ty: "el",          // 원
        s: { a: 0, k: [80, 80] },
        p: { a: 0, k: [0, 0] }
      }, {
        ty: "st",          // 테두리
        c: { a: 0, k: [0.2, 0.6, 1, 1] },  // RGBA
        w: { a: 0, k: 3 }
      }]
    }
  ]
};
```

## 주요 옵션

| 옵션 | 값 | 설명 |
|------|-----|------|
| `renderer` | `'svg'` | SVG가 가장 깔끔. Canvas는 성능 우선 |
| `loop` | `false` | 결과 공개 연출은 1회만 |
| `autoplay` | `true` | 컨테이너가 보일 때 자동 재생 |
| `animationData` | `{}` | 인라인 JSON (path 대신 사용) |

## 삽질 방지

- **인라인 JSON vs 외부 파일** — 간단한 애니메이션은 인라인이 편함 (HTTP 요청 절약)
- **`animationData`와 `path` 동시 사용 금지** — 둘 중 하나만
- **컨테이너 크기 지정** — width/height 없으면 0px로 렌더링
- **`destroy()` 호출** — SPA에서 화면 전환 시 `anim.destroy()` 필수 (메모리 누수)
- **복잡한 애니메이션은 LottieFiles에서 다운로드** — 직접 JSON 작성은 간단한 것만
