# [OG] Open Graph 메타태그

> 카카오톡/페이스북/트위터 공유 시 미리보기.

## 기본 태그 세트

```html
<meta property="og:type" content="website">
<meta property="og:title" content="앱 제목 - 한줄 설명">
<meta property="og:description" content="공유 시 보이는 설명문">
<meta property="og:url" content="https://subdomain.pearsoninsight.com">
<meta property="og:image" content="https://subdomain.pearsoninsight.com/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="앱 제목">
<meta name="twitter:description" content="설명문">
<meta name="twitter:image" content="https://subdomain.pearsoninsight.com/og-image.png">
```

## 결과별 OG 이미지 동적 교체

```javascript
function updateOgImage(imageUrl) {
  const ogImg = document.querySelector('meta[property="og:image"]');
  const twImg = document.querySelector('meta[name="twitter:image"]');
  if (ogImg) ogImg.setAttribute('content', imageUrl);
  if (twImg) twImg.setAttribute('content', imageUrl);
}

// 결과 표시 시
updateOgImage(`${location.origin}/og-${grade.id}.png`);
```

## 이미지 규격

| 항목 | 값 |
|------|-----|
| 크기 | 1200 x 630px |
| 포맷 | PNG |
| 용량 | 300KB 이하 권장 |
| 텍스트 | 중앙에 크게, 모바일에서도 읽히게 |

## 주의사항

- 카카오톡은 OG 이미지를 **캐싱**함 → 이미지 변경 시 URL도 변경 필요 (`?v=2`)
- `og:url`은 **canonical URL** (결과 페이지가 아닌 메인)
- 이미지 URL은 반드시 **https 절대경로**
