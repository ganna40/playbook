# [SCREEN] 화면 전환 시스템

> 인트로 → 진행(질문/입력) → 결과 화면 전환.

## HTML 구조

```html
<div id="app">
  <div id="screen-intro" class="screen active">
    <!-- 인트로: 제목 + 설명 + 시작 버튼 -->
  </div>
  <div id="screen-progress" class="screen">
    <!-- 진행: 질문 또는 입력 -->
  </div>
  <div id="screen-result" class="screen">
    <!-- 결과: 등급 카드 + 공유 -->
  </div>
</div>
```

## JavaScript

```javascript
function showScreen(name) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  const target = document.getElementById(`screen-${name}`);
  target.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// 사용
document.getElementById('btn-start').onclick = () => showScreen('progress');
```

## CSS

```css
.screen { display: none }
.screen.active {
  display: block;
  animation: fadeIn 0.35s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px) }
  to { opacity: 1; transform: none }
}
```

## 인트로 화면 패턴

```html
<div id="screen-intro" class="screen active">
  <div class="intro-top">
    <div class="intro-logo">앱 <span>제목</span></div>
    <div class="intro-desc">한줄 설명</div>
  </div>
  <button class="btn-start" onclick="showScreen('progress'); initQuiz();">
    시작하기
  </button>
</div>
```

## 결과 화면 패턴

```html
<div id="screen-result" class="screen">
  <div id="result-card" class="result-card">
    <!-- [GRADE] 모듈이 채움 -->
  </div>
  <div class="share-buttons">
    <!-- [SHARE] 모듈 -->
  </div>
  <button class="btn-retry" onclick="location.reload()">다시 하기</button>
</div>
```
