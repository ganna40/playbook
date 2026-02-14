# [GRADE] 등급/티어 시스템

> 점수 → 등급 매핑 + 결과 카드 생성.
> 모든 바이럴 앱에서 공통 사용.

## 데이터 구조

```json
{
  "grades": [
    {"min": 0,  "max": 8,   "id": "S",  "name": "시그마", "emoji": "🐺", "color": "#c0c0c0", "ogImage": "og-Sigma.png"},
    {"min": 9,  "max": 20,  "id": "A",  "name": "알파",   "emoji": "🦁", "color": "#ffd700", "ogImage": "og-Alpha.png"},
    {"min": 21, "max": 40,  "id": "B",  "name": "베타",   "emoji": "🐕", "color": "#3b82f6", "ogImage": "og-Beta.png"},
    {"min": 41, "max": 60,  "id": "C",  "name": "감마",   "emoji": "🦊", "color": "#f97316", "ogImage": "og-Gamma.png"},
    {"min": 61, "max": 80,  "id": "D",  "name": "델타",   "emoji": "🐑", "color": "#ef4444", "ogImage": "og-Delta.png"},
    {"min": 81, "max": 100, "id": "F",  "name": "오메가", "emoji": "🐁", "color": "#7f1d1d", "ogImage": "og-Omega.png"}
  ]
}
```

## 등급 판정

```javascript
function determineGrade(score) {
  const grades = quizData.grades;
  for (const g of grades) {
    if (score >= g.min && score <= g.max) return g;
  }
  return grades[grades.length - 1]; // fallback: 최하위
}
```

## 결과 카드 생성

```javascript
function showResult(grade, score, details) {
  const card = document.getElementById('result-card');
  card.innerHTML = `
    <div class="grade-badge" style="background:${grade.color}20; border:2px solid ${grade.color}">
      <span class="grade-emoji">${grade.emoji}</span>
      <span class="grade-name" style="color:${grade.color}">${grade.name}</span>
    </div>
    <div class="grade-title">${grade.title || grade.name}</div>
    <div class="grade-desc">${grade.desc || ''}</div>
    <div class="grade-score">점수: ${score}점</div>
  `;

  // OG 이미지 동적 변경 (공유 시 결과별 이미지)
  document.querySelector('meta[property="og:image"]')
    ?.setAttribute('content', location.origin + '/' + grade.ogImage);

  showScreen('result');
}
```

## 결과 카드 CSS

```css
.result-card {
  background: var(--card);
  border-radius: 20px;
  padding: 32px 24px;
  text-align: center;
}
.grade-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  border-radius: 100px;
  margin-bottom: 16px;
}
.grade-emoji { font-size: 24px }
.grade-name { font-size: 18px; font-weight: 700 }
.grade-title {
  font-size: 22px;
  font-weight: 800;
  margin: 12px 0;
}
.grade-desc {
  font-size: 15px;
  color: var(--t2);
  line-height: 1.7;
}
```

## 등급별 OG 이미지 규칙

| 파일명 패턴 | 크기 | 용도 |
|-------------|------|------|
| `og-image.png` | 1200x630 | 기본 (메인 공유) |
| `og-{등급명}.png` | 1200x630 | 결과별 공유 이미지 |

등급 수만큼 OG 이미지 필요. 각 이미지에 등급명 + 한줄 설명 포함.
