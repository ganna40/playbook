# [QUIZ] 퀴즈/설문 엔진

> O/X 또는 선택형 질문 → 점수 계산 → 등급 판정.
> pong, mz, amlife에서 사용된 패턴.

## 데이터 구조 (data.json)

### O/X 방식 (pong 스타일)

```json
{
  "categories": [
    {"id": "A", "name": "카테고리명", "color": "#a855f7", "emoji": "🧠"}
  ],
  "questions": [
    {
      "id": "A1",
      "c": "A",
      "q": "질문 텍스트",
      "bs": 3,
      "killer": true
    }
  ],
  "grades": [
    {"min": 0, "max": 20, "g": "S", "name": "최상위", "emoji": "🦁"}
  ]
}
```

| 필드 | 의미 |
|------|------|
| `c` | 카테고리 ID |
| `bs` | 기본 점수 (O 선택 시 획득) |
| `killer` | true면 콤보/상관관계에서 가중치 부여 |

### 선택형 (mz/amlife 스타일)

```json
{
  "questions": [
    {
      "id": "Q1",
      "c": "카테고리",
      "q": "질문 텍스트",
      "options": [
        {"text": "선택지1", "score": 0},
        {"text": "선택지2", "score": 1},
        {"text": "선택지3", "score": 2}
      ]
    }
  ]
}
```

## 핵심 로직

### 1. 데이터 로드

```javascript
let quizData = null;

async function loadData() {
  const res = await fetch('data.json');
  quizData = await res.json();
  initQuiz();
}
```

### 2. 퀴즈 진행 관리

```javascript
let currentIndex = 0;
let answers = {};

function showQuestion(index) {
  const q = quizData.questions[index];
  document.getElementById('question-text').textContent = q.q;
  document.getElementById('question-counter').textContent =
    `${index + 1} / ${quizData.questions.length}`;

  // 프로그레스 바
  const pct = ((index + 1) / quizData.questions.length) * 100;
  document.getElementById('progress-bar').style.width = pct + '%';
}

function selectAnswer(value) {
  const q = quizData.questions[currentIndex];
  answers[q.id] = value;

  currentIndex++;
  if (currentIndex >= quizData.questions.length) {
    calculateResult();
  } else {
    showQuestion(currentIndex);
  }
}
```

### 3. 점수 계산 (O/X)

```javascript
function calculateResult() {
  let totalScore = 0;
  const categoryScores = {};

  // 기본 점수
  for (const [qId, answered] of Object.entries(answers)) {
    if (!answered) continue;  // X는 스킵
    const q = quizData.questions.find(q => q.id === qId);
    totalScore += q.bs;
    categoryScores[q.c] = (categoryScores[q.c] || 0) + q.bs;
  }

  // 콤보 보너스 (선택)
  if (quizData.combos) {
    for (const combo of quizData.combos) {
      if (combo.ids.every(id => answers[id])) {
        totalScore += combo.bonus;
      }
    }
  }

  // 등급 판정 → [GRADE] 모듈
  const grade = determineGrade(totalScore);
  showResult(grade, totalScore, categoryScores);
}
```

### 4. 점수 계산 (선택형)

```javascript
function calculateResult() {
  let totalScore = 0;
  const categoryScores = {};
  const maxByCategory = {};

  for (const q of quizData.questions) {
    const selected = answers[q.id];
    if (selected === undefined) continue;
    totalScore += selected;
    categoryScores[q.c] = (categoryScores[q.c] || 0) + selected;
    const maxScore = Math.max(...q.options.map(o => o.score));
    maxByCategory[q.c] = (maxByCategory[q.c] || 0) + maxScore;
  }

  // 카테고리별 백분율 (레이더 차트용)
  const percentages = {};
  for (const [cat, score] of Object.entries(categoryScores)) {
    percentages[cat] = Math.round((score / maxByCategory[cat]) * 100);
  }

  const grade = determineGrade(totalScore);
  showResult(grade, totalScore, percentages);
}
```

## 프로그레스 바 CSS

```css
.progress-wrap {
  background: rgba(255,255,255,0.1);
  border-radius: 100px;
  height: 6px;
  overflow: hidden;
  margin-bottom: 24px;
}
.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  border-radius: 100px;
  transition: width 0.3s ease;
}
```

## 질문 전환 애니메이션

```css
@keyframes slideIn {
  from { opacity: 0; transform: translateX(20px) }
  to { opacity: 1; transform: translateX(0) }
}
.question-card { animation: slideIn 0.3s ease }
```
