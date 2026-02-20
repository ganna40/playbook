# TOURNAMENT - 토너먼트 월드컵 엔진

> 이상형 월드컵, 음식 월드컵 등 N강 토너먼트 대결 앱에 사용.
> 의존: BASE, SCREEN

## 개요

QUIZ 모듈이 점수 누적 방식이라면, TOURNAMENT는 **1:1 대결 탈락** 방식.
64명 → 32명 → 16명 → ... → 결승 → 우승자 1명.

## 핵심 코드

### 데이터 형식

```javascript
// 파이프(|) 구분 인라인 데이터
const RAW = "항목1,그룹1|항목2,그룹2|항목3,그룹3|...";

function parseData(raw, prefix) {
  return raw.split('|').map((s, i) => {
    const p = s.indexOf(',');
    return { n: s.slice(0, p), g: s.slice(p + 1), id: i + 1, pf: prefix };
  });
}
const ITEMS = parseData(RAW, 'a'); // [{n:"항목1", g:"그룹1", id:1, pf:"a"}, ...]
```

### 토너먼트 상태

```javascript
let pool = [], picks = [], matchIdx = 0, roundSize = 64;

function shuffle(a) {
  const b = [...a];
  for (let i = b.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [b[i], b[j]] = [b[j], b[i]];
  }
  return b;
}
```

### 게임 시작 + 이미지 프리로딩

```javascript
function preloadAll(list) {
  return new Promise(resolve => {
    let loaded = 0; const total = list.length;
    if (total === 0) return resolve();
    list.forEach(c => {
      const i = new Image();
      i.onload = i.onerror = () => { loaded++; if (loaded >= total) resolve() };
      i.src = getImgPath(c);
    });
    setTimeout(resolve, 8000); // 최대 8초 타임아웃
  });
}

function startGame() {
  loadingOverlay.style.display = 'flex';
  preloadAll(data).then(() => {
    loadingOverlay.style.display = 'none';
    pool = shuffle(data);
    picks = []; matchIdx = 0; roundSize = data.length;
    showScreen('matchScreen');
    renderMatch();
  });
}
```

### 매치 렌더링

```javascript
function getImgPath(c) { return 'img/' + c.pf + '/' + c.id + '.jpg?v=1' }

function renderMatch() {
  const a = pool[matchIdx * 2], b = pool[matchIdx * 2 + 1];
  const total = pool.length / 2;

  // 라운드 표시
  const rn = roundSize === 2 ? '결승' : (roundSize + '강');
  roundBadge.textContent = rn;
  matchCount.textContent = (matchIdx + 1) + '/' + total;
  progressFill.style.width = ((matchIdx + 1) / total * 100) + '%';

  setCard(0, a);
  setCard(1, b);

  // 다음 매치 프리로드
  if (matchIdx + 1 < total) {
    new Image().src = getImgPath(pool[(matchIdx + 1) * 2]);
    new Image().src = getImgPath(pool[(matchIdx + 1) * 2 + 1]);
  }
}
```

### 선택 처리

```javascript
function pick(side) {
  if (isAnimating) return;
  isAnimating = true;
  const winner = pool[matchIdx * 2 + side];
  picks.push(winner);

  // 선택/탈락 애니메이션
  document.getElementById('card' + side).classList.add('selected');
  document.getElementById('card' + (1 - side)).classList.add('rejected');

  setTimeout(() => {
    matchIdx++;
    if (matchIdx >= pool.length / 2) {
      // 라운드 종료
      if (picks.length === 1) { showWinner(picks[0]); isAnimating = false; return; }
      pool = [...picks]; picks = []; roundSize = pool.length; matchIdx = 0;
      // 라운드 전환 연출
      showScreen('roundScreen');
      setTimeout(() => { showScreen('matchScreen'); renderMatch(); isAnimating = false; }, 1000);
      return;
    }
    renderMatch(); isAnimating = false;
  }, 350);
}
```

## CSS

```css
/* 카드 이미지 래퍼 - aspect-ratio로 비율 고정 */
.card-img-wrap { position:relative; overflow:hidden; aspect-ratio:2/3; }
.card-img-wrap img { width:100%; height:100%; object-fit:cover; object-position:center 30%; }

/* 선택/탈락 상태 */
.candidate-card.selected { border-color:var(--gold); box-shadow:0 0 40px rgba(251,191,36,.4); }
.candidate-card.rejected { filter:grayscale(1) brightness(.4); opacity:.4; }

/* VS 뱃지 */
.vs-badge { position:absolute; left:50%; top:42%; transform:translate(-50%,-50%);
  width:44px; height:44px; background:linear-gradient(135deg,var(--gold),var(--gold2));
  border-radius:50%; display:flex; align-items:center; justify-content:center;
  font-weight:900; font-size:15px; z-index:10; }
```

## 주의사항

- **이미지 프리로딩 필수**: 64장 동시 로드, 타임아웃 8초 설정
- **isAnimating 가드**: 연타 방지 (애니메이션 중 클릭 무시)
- **aspect-ratio: 2/3**: flex:1 대신 사용해야 이미지 크롭 최소화
- **object-position: center 30%**: 인물 사진 상단 집중 (얼굴 위치)
- **캐시 버스팅**: `?v=N` 파라미터로 이미지 갱신 관리
- **이미지 폴백**: img.onerror 시 텍스트 카드로 대체

## 사용 예시

```javascript
// 이상형 월드컵: 성별 분기
function startGame(gender) {
  const data = gender === 'm' ? [...WOMEN] : [...MEN];
  // ... 이하 동일
}

// 음식 월드컵: 단일 리스트
function startGame() {
  const data = [...FOODS]; // 64개 음식
  // ... 이하 동일
}
```
