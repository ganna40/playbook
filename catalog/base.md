# [BASE] SPA 기본 골격

> 단일 HTML 파일 기반 모바일 웹앱의 뼈대.
> 빌드 도구 없이 바로 실행 가능.

## 파일 구조
```
project/
├── index.html      # 앱 전체 (HTML + CSS + JS)
├── data.json       # 콘텐츠 데이터 (선택)
├── og-image.png    # 기본 공유 이미지
└── og-*.png        # 결과별 공유 이미지
```

## 기본 HTML 골격

```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>앱 제목</title>

<!-- [OG] 모듈 삽입 위치 -->
<!-- [GA] 모듈 삽입 위치 -->
<!-- [KAKAO] SDK 삽입 위치 -->

<style>
  /* [STYLE-*] 모듈 삽입 위치 */
  *, *::before, *::after { box-sizing: border-box }
  body { margin: 0; padding: 0; min-height: 100vh; overflow-x: hidden }
  #app { max-width: 480px; width: 100%; margin: 0 auto; padding: 0 20px 40px }
  .screen { display: none }
  .screen.active { display: block; animation: fadeIn 0.35s ease }
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px) }
    to { opacity: 1; transform: none }
  }
</style>
</head>
<body>
<div id="app">
  <div id="screen-intro" class="screen active"><!-- 인트로 --></div>
  <div id="screen-progress" class="screen"><!-- 진행 --></div>
  <div id="screen-result" class="screen"><!-- 결과 --></div>
</div>

<script>
// [DATA] 모듈: 데이터 로드
// [SCREEN] 모듈: 화면 전환
// [QUIZ] 또는 [CALC] 모듈: 핵심 로직
// [SHARE] 모듈: 공유 기능
</script>
</body>
</html>
```

## 핵심 규칙

| 규칙 | 이유 |
|------|------|
| `max-width: 480px` | 모바일 최적화 (카톡 공유 타겟) |
| `user-scalable=no` | 줌 방지 (앱 느낌) |
| 단일 HTML | 서버에 파일 하나만 올리면 끝 |
| CDN 라이브러리 | npm/빌드 불필요 |
