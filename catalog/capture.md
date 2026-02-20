# [CAPTURE] 결과 이미지 캡처

> html2canvas로 결과 화면을 PNG 이미지로 변환 + 다운로드.
> 인스타 스토리, 카톡 공유용 이미지 생성.

## CDN

```html
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
```

## 핵심 로직 (완전판)

```javascript
function captureResult() {
  const el = document.getElementById('resultCapture'); // 캡처 대상 영역
  const btn = document.getElementById('btnCapture');
  btn.textContent = '📸 캡처 중...';
  btn.disabled = true;

  /* ① Canvas 레이더가 있으면 애니메이션 없이 완전 상태로 다시 그리기 */
  // drawRadar(color, false) — false = 애니메이션 스킵, 즉시 최종 상태
  // 예: drawRadar(RESULTS[currentKey].radarColor, false);

  /* ② 약간의 딜레이 후 캡처 (DOM 반영 대기) */
  setTimeout(() => {
    html2canvas(el, {
      backgroundColor: '#0c0614',  // 다크 테마면 배경색 명시
      scale: 2,                     // 고해상도 (2x)
      useCORS: true,                // 외부 이미지 허용
      logging: false,

      /* ③ onclone: 캡처 직전 클론 DOM 수정 (원본 안 건드림) */
      onclone: (clonedDoc) => {
        const wrap = clonedDoc.getElementById('resultCapture');

        /* 모든 CSS 애니메이션 → 최종 상태로 강제 */
        wrap.querySelectorAll('*').forEach(node => {
          const cs = getComputedStyle(node);
          if (cs.animationName && cs.animationName !== 'none') {
            node.style.animation = 'none';
            node.style.opacity = '1';
            node.style.transform = 'none';
          }
        });

        /* backdrop-filter 제거 (html2canvas 미지원) */
        wrap.querySelectorAll('[style*="backdrop"],.char-badge').forEach(el => {
          el.style.backdropFilter = 'none';
          el.style.webkitBackdropFilter = 'none';
        });

        /* CSS 변수 → 실제 값으로 인라인 (html2canvas 호환) */
        const rs = getComputedStyle(document.documentElement);
        ['--bg','--card','--card2','--border','--t1','--t2','--t3',
         '--pink','--pink2','--pink3','--purple','--purple2','--purple3',
         '--gold','--gold2','--green','--red'].forEach(v => {
          clonedDoc.documentElement.style.setProperty(v, rs.getPropertyValue(v));
        });
      }
    }).then(canvas => {
      const link = document.createElement('a');
      link.download = '결과이미지.png';
      link.href = canvas.toDataURL('image/png');
      link.click();

      btn.textContent = '✅ 저장됨!';
      setTimeout(() => { btn.textContent = '📸 이미지 저장'; btn.disabled = false; }, 2000);
    }).catch(() => {
      btn.textContent = '📸 이미지 저장';
      btn.disabled = false;
    });
  }, 80);
}
```

## HTML 버튼

```html
<button class="btn-share" id="btnCapture" onclick="captureResult()">📸 이미지 저장</button>
```

## 주요 옵션

| 옵션 | 값 | 설명 |
|------|-----|------|
| `backgroundColor` | `#0c0614` | 투명 방지, 테마 배경색 |
| `scale` | `2` | 2x 해상도 (인스타용) |
| `useCORS` | `true` | 외부 이미지 CORS 허용 |
| `logging` | `false` | 콘솔 로그 비활성 |

## 삽질 방지

- **캡처 영역을 별도 div로 감싸기** — 공유 버튼 등은 캡처에서 제외
- **외부 폰트 주의** — CDN 폰트가 로드 안 된 상태에서 캡처하면 기본 폰트로 나옴. 결과 화면 진입 후 충분한 딜레이 후 캡처
- **모바일 Safari** — `canvas.toDataURL`이 큰 이미지에서 실패할 수 있음. `scale: 1`로 줄이기

### ⚠️ html2canvas 미지원 / 렌더링 깨지는 것들

| 항목 | 증상 | 해결법 |
|------|------|--------|
| **CSS 애니메이션** | 캡처 시점의 중간 상태가 찍힘 (투명, 위치 어긋남) | `onclone`에서 `animation:none; opacity:1; transform:none` 강제 |
| **`backdrop-filter: blur`** | 완전히 무시됨 (투명하게 나옴) | `onclone`에서 제거하고 `background` 불투명으로 교체 |
| **CSS 변수 `var()`** | 일부 환경에서 미해석 → 투명/기본값 | `onclone`에서 `getComputedStyle`로 실제 값 인라인 |
| **Canvas 애니메이션** | `requestAnimationFrame` 중간 프레임 캡처 | 캡처 직전 `drawRadar(color, false)` — 애니메이션 없이 최종 상태 렌더 |
| **`linear-gradient` + `var()`** | 그라데이션 안에 CSS 변수 → 깨짐 | CSS 변수 인라인 처리로 해결 |
| **외부 이미지** | CORS 에러로 빈 이미지 | `useCORS: true` + 이미지 서버 CORS 헤더 |
| **`position: fixed`** | 레이아웃 어긋남 | 캡처 영역 내에 `fixed` 요소 넣지 말 것 |

### Canvas 레이더 차트 + 캡처 함께 쓸 때

`drawRadar(color)` 함수에 `animate` 파라미터를 추가해야 함:

```javascript
function drawRadar(color, animate) {
  // ... setup ...

  function renderFrame(ease) {
    // 그리기 로직 (ease 0~1)
  }

  if (animate === false) {
    renderFrame(1);  // 즉시 완전 상태
    return;
  }

  // 기본: 애니메이션
  let progress = 0;
  function frame() {
    progress = Math.min(1, progress + 0.055);
    renderFrame(1 - Math.pow(1 - progress, 3));
    if (progress < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}
```

캡처 전: `drawRadar(RESULTS[currentKey].radarColor, false);`

### `onclone` 체크리스트 (매번 확인)

1. ✅ 모든 애니메이션 `animation: none; opacity: 1; transform: none`
2. ✅ `backdrop-filter` 제거
3. ✅ CSS 변수 인라인 (`--bg`, `--card`, 색상 전부)
4. ✅ Canvas 레이더 정적 렌더링 (`animate: false`)
5. ✅ `setTimeout(80)` 딜레이 (DOM 반영 대기)
