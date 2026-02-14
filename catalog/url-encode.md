# [URL-ENCODE] 결과 URL 공유

> 결과를 URL 파라미터에 인코딩해서 공유.
> 링크 받은 사람이 바로 결과 화면을 볼 수 있음.
> mz, amlife에서 사용.

## 인코딩 (결과 → URL)

```javascript
// 답변 배열을 문자열로 압축
function encodeResult() {
  const answers = st.answers.map(a => a >= 0 ? a : 0).join('');
  const params = new URLSearchParams();
  params.set('a', st.age || 25);       // 나이
  params.set('g', st.gender || 'M');   // 성별
  params.set('r', answers);             // 답변 (0123012301...)
  return location.origin + location.pathname + '?' + params.toString();
}

// 공유 시
function copyResultUrl() {
  const url = encodeResult();
  navigator.clipboard.writeText(url);
  showToast('링크가 복사되었습니다');
}
```

## 디코딩 (URL → 결과 바로 표시)

```javascript
function decodeURL() {
  const params = new URLSearchParams(location.search);
  const r = params.get('r');
  const a = params.get('a');
  const g = params.get('g');

  if (r && r.length === totalQuestions) {
    st.answers = r.split('').map(Number);
    st.age = parseInt(a) || 25;
    st.gender = g || 'M';
    st.shared = true;
    return true; // → 바로 결과 화면으로
  }
  return false; // → 인트로부터 시작
}

// 앱 시작 시
if (!decodeURL()) {
  showScreen('intro');
} else {
  showScreen('result');
}
```

## MZ 방식 (더 간단)

```javascript
// 인코딩: 출생연도(4자리) + 답변(1자리씩)
function getShareURL() {
  return 'https://mz.pearsoninsight.com/?d=' +
    birthYear + answers.map(a => a - 1).join('');
}
// 예: ?d=199502101230...  (1995년생 + 40개 답변)

// 디코딩
const d = params.get('d');
if (d && d.length === 44) {  // 4(연도) + 40(답변)
  birthYear = parseInt(d.substring(0, 4));
  answers = d.substring(4).split('').map(c => parseInt(c) + 1);
  showResult();
}
```

## 주의사항

- URL 길이 제한: 2,048자 이내 (대부분 브라우저)
- 답변이 0~4면 1자리로 충분, 10 이상이면 다른 인코딩 필요
- 공유 URL은 `history.replaceState`로 정리
```javascript
// 결과 표시 후 URL 파라미터 제거 (재시작 시 인트로부터)
function restart() {
  history.replaceState(null, '', location.pathname);
  showScreen('intro');
}
```
