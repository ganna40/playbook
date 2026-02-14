# [GA] Google Analytics

> 방문자 트래킹. 바이럴 성과 측정용.

## 설치 코드

```html
<!-- <head> 최상단에 삽입 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-XXXXXXXXXX');
</script>
```

> 현재 사용 중인 ID: 로컬 `_secrets.md` 참조

## 커스텀 이벤트 (선택)

```javascript
// 결과 도달 시
gtag('event', 'quiz_complete', {
  grade: grade.name,
  score: score
});

// 공유 클릭 시
gtag('event', 'share', {
  method: 'kakao',  // 또는 'url_copy', 'screenshot'
  content_type: 'result'
});
```

## Google Analytics 설정

1. https://analytics.google.com 접속
2. 관리 → 속성 만들기 → 웹 스트림 추가
3. 측정 ID (`G-XXXXXXXXXX`) 복사
4. 위 코드에 삽입
