# [KAKAO] 카카오톡 공유

> 카카오톡으로 결과를 공유하는 기능.
> Kakao JS SDK 사용.

## SDK 로드

```html
<script src="https://t1.kakaocdn.net/kakao_js_sdk/2.7.4/kakao.min.js"></script>
```

## 초기화

```javascript
// 앱 시작 시 1회 호출
if (window.Kakao && !Kakao.isInitialized()) {
  Kakao.init('YOUR_KAKAO_APP_KEY');
}
```

> **Kakao Developers** (https://developers.kakao.com) 에서 앱 생성 후 JavaScript 키 사용.
> 플랫폼 설정에서 도메인 등록 필수.

## 앱별 Kakao 키

| 앱 | 키 |
|-----|-----|
| salary | `d374df0ebf74958122e78977437aff4d` |
| pong | `f73d82313342c09563c22a9b884b0dd4` |
| mz | `f856cfaf6a221e0565604457f67d8ee8` |
| amlife | `217c7f6152efeadb73c8eeaf193edcb7` |

## 공유 함수

### 기본형 (텍스트 + 링크 + 이미지)

```javascript
function shareKakao(resultData) {
  Kakao.Share.sendDefault({
    objectType: 'feed',
    content: {
      title: resultData.title,         // "당신의 등급: 알파"
      description: resultData.desc,     // "관계의 주도자..."
      imageUrl: resultData.ogImage,     // "https://도메인/og-Alpha.png"
      link: {
        mobileWebUrl: window.location.href,
        webUrl: window.location.href
      }
    },
    buttons: [{
      title: '나도 해보기',
      link: {
        mobileWebUrl: 'https://도메인/',  // 메인 페이지로
        webUrl: 'https://도메인/'
      }
    }]
  });
}
```

### 점수 포함형 (salary 스타일)

```javascript
function shareKakao(title, desc, imageUrl, buttonText) {
  if (!Kakao.isInitialized()) Kakao.init('YOUR_KEY');
  Kakao.Share.sendDefault({
    objectType: 'feed',
    content: {
      title: title,
      description: desc,
      imageUrl: imageUrl,
      link: {
        mobileWebUrl: location.origin,
        webUrl: location.origin
      }
    },
    buttons: [{
      title: buttonText || '나도 해보기',
      link: {
        mobileWebUrl: location.origin,
        webUrl: location.origin
      }
    }]
  });
}
```

## 주의사항

- `Kakao.init()`은 **1회만** 호출 (중복 호출 시 에러)
- `Kakao.isInitialized()`로 체크 후 호출
- 도메인이 Kakao Developers에 등록 안 되면 공유 실패
- `imageUrl`은 **절대 경로** (https://...) 필수
- OG 이미지 권장 크기: **1200x630px**
