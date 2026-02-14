# [SHARE] 통합 공유 시스템

> 카카오톡 + URL 복사 + 스크린샷 저장을 하나로.
> 의존: [KAKAO], [OG]

## 필요 라이브러리

```html
<!-- 카카오 SDK -->
<script src="https://t1.kakaocdn.net/kakao_js_sdk/2.7.4/kakao.min.js"></script>
<!-- 스크린샷용 -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
```

## 공유 버튼 UI

```html
<div class="share-buttons">
  <button onclick="shareKakao()">카카오톡 공유</button>
  <button onclick="copyUrl()">링크 복사</button>
  <button onclick="saveImage()">이미지 저장</button>
</div>
```

## 1. 카카오 공유

→ [KAKAO 모듈](kakao.md) 참조

## 2. URL 복사

```javascript
function copyUrl() {
  const url = window.location.origin;  // 또는 결과 공유 URL
  navigator.clipboard.writeText(url).then(() => {
    showToast('링크가 복사되었습니다!');
  }).catch(() => {
    // fallback (iOS 등)
    const ta = document.createElement('textarea');
    ta.value = url;
    ta.style.cssText = 'position:fixed;opacity:0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast('링크가 복사되었습니다!');
  });
}

function showToast(msg) {
  const toast = document.createElement('div');
  toast.textContent = msg;
  toast.style.cssText = `
    position:fixed;bottom:80px;left:50%;transform:translateX(-50%);
    background:#333;color:#fff;padding:12px 24px;border-radius:8px;
    font-size:14px;z-index:9999;animation:fadeIn .3s ease
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 2000);
}
```

## 3. 결과 카드 스크린샷 저장

```javascript
async function saveImage() {
  const card = document.getElementById('result-card');

  // 저장 전 버튼 숨기기
  const buttons = card.querySelectorAll('.share-buttons');
  buttons.forEach(b => b.style.display = 'none');

  try {
    const canvas = await html2canvas(card, {
      scale: 2,                    // 고해상도
      backgroundColor: '#0a0a0f', // 배경색 (테마에 맞게)
      useCORS: true,              // 외부 이미지 허용
      logging: false
    });

    const link = document.createElement('a');
    link.download = '결과.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
  } finally {
    buttons.forEach(b => b.style.display = '');
  }
}
```

## 4. 공유 버튼 스타일 (다크)

```css
.share-buttons {
  display: flex;
  gap: 8px;
  margin-top: 20px;
}
.share-buttons button {
  flex: 1;
  padding: 14px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.1s;
}
.share-buttons button:active { transform: scale(0.97) }
.share-buttons button:nth-child(1) { background: #FEE500; color: #191919 } /* 카카오 */
.share-buttons button:nth-child(2) { background: #3b82f6; color: #fff }    /* 링크복사 */
.share-buttons button:nth-child(3) { background: #374151; color: #fff }    /* 이미지 */
```

## 주의사항

- `html2canvas`는 **외부 이미지에 CORS 필요** → `useCORS: true`
- iOS Safari에서 `navigator.clipboard` 안 될 수 있음 → fallback 필수
- 스크린샷 전에 공유 버튼 숨기기 (안 하면 버튼도 캡처됨)
- `scale: 2` 로 고해상도 캡처 (안 하면 흐릿함)
