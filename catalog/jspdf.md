# [JSPDF] PDF 생성 — jsPDF + html2canvas

> 웹페이지 화면을 "사진 찍어서" PDF 파일로 만들어주는 기술.
> 화면을 먼저 이미지로 찍고(html2canvas), 그 이미지를 PDF 문서에 붙여넣기(jsPDF)하는 방식.
> 한글이 깨지지 않고 예쁘게 나오며, 페이지가 길면 자동으로 여러 장으로 나눠준다.

## CDN

```html
<script src="https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
```

## 핵심 로직

```javascript
function generatePDF() {
  const btn = document.getElementById('btnPDF');
  btn.textContent = '📄 생성 중...';
  btn.disabled = true;

  /* ① 숨겨진 HTML 레이아웃 생성 (한글 포함) */
  const wrap = document.createElement('div');
  wrap.style.cssText = 'position:fixed;left:-9999px;top:0;width:800px;padding:40px;background:#fff;font-family:Pretendard,sans-serif;color:#222;';
  wrap.innerHTML = buildPDFContent(); // 한글 HTML 콘텐츠
  document.body.appendChild(wrap);

  /* ② html2canvas로 렌더링 */
  html2canvas(wrap, {
    scale: 2,
    backgroundColor: '#ffffff',
    useCORS: true,
    logging: false
  }).then(canvas => {
    document.body.removeChild(wrap);

    /* ③ 멀티 페이지 A4 PDF 생성 */
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pageW = 210;
    const pageH = 297;
    const margin = 10;
    const contentW = pageW - margin * 2;

    const imgW = canvas.width;
    const imgH = canvas.height;
    const ratio = contentW / imgW;
    const totalH = imgH * ratio;
    const maxH = pageH - margin * 2;

    let y = 0;
    let page = 0;

    while (y < totalH) {
      if (page > 0) pdf.addPage();

      const srcY = y / ratio;
      const sliceH = Math.min(maxH, totalH - y);
      const srcSliceH = sliceH / ratio;

      /* ④ 캔버스 슬라이스 */
      const sliceCanvas = document.createElement('canvas');
      sliceCanvas.width = imgW;
      sliceCanvas.height = srcSliceH;
      sliceCanvas.getContext('2d').drawImage(
        canvas, 0, srcY, imgW, srcSliceH, 0, 0, imgW, srcSliceH
      );

      pdf.addImage(
        sliceCanvas.toDataURL('image/png'),
        'PNG', margin, margin, contentW, sliceH
      );

      y += maxH;
      page++;
    }

    pdf.save('결과.pdf');
    btn.textContent = '✅ 저장됨!';
    setTimeout(() => { btn.textContent = '📄 PDF 저장'; btn.disabled = false; }, 2000);
  }).catch(() => {
    document.body.removeChild(wrap);
    btn.textContent = '📄 PDF 저장';
    btn.disabled = false;
  });
}
```

## 삽질 방지

- **jsPDF 내장 폰트(Helvetica)는 한글 미지원** — 한글이 깨짐. html2canvas로 이미지화 후 삽입이 정답
- **CDN 버전 주의** — jsPDF v2.5.2는 존재하지 않음. **v2.5.1** 사용
- **cdnjs vs jsdelivr** — cdnjs에서 404 나면 jsdelivr로 교체
- **멀티 페이지 처리** — A4 높이(297mm) 초과 시 캔버스를 슬라이스해서 `addPage()` 사용
- **숨겨진 div 정리** — catch에서도 반드시 `removeChild` 호출
- **Service Worker 캐싱** — CDN URL 변경 후 SW가 이전 버전 캐싱 → 캐시 버전 올려야 함
