# [CALC] 계산기 엔진

> 숫자 입력 → 계산 → 결과 표시.
> salary(월급계산기)에서 사용된 패턴.

## 데이터 구조 (data.json)

```json
{
  "year": 2026,
  "rates": {
    "nationalPension": 0.0475,
    "healthInsurance": 0.03595,
    "longTermCare": 0.1314,
    "employmentInsurance": 0.009,
    "localTaxRate": 0.1
  },
  "taxTable": [[83, 0], [92, 0], [100, 0], [125, 800]],
  "salaryTable": [
    {"percentile": 10, "amount": 200},
    {"percentile": 25, "amount": 280}
  ],
  "tiers": [
    {"min": 0, "max": 200, "name": "Iron", "color": "#8B8B8B"}
  ]
}
```

## 핵심 패턴

### 1. 입력 UI (빠른 선택 + 직접입력)

```html
<div class="quick-buttons">
  <button onclick="setAmount(200)">200만</button>
  <button onclick="setAmount(300)">300만</button>
  <button onclick="setAmount(500)">500만</button>
</div>
<input type="text" id="salary-input" inputmode="numeric"
       placeholder="월급을 입력하세요 (만원)">
```

```javascript
function setAmount(val) {
  document.getElementById('salary-input').value = val;
  calculate();
}
```

### 2. 숫자 포맷팅 (실시간)

```javascript
const input = document.getElementById('salary-input');
input.addEventListener('input', (e) => {
  // 숫자만 남기기
  let val = e.target.value.replace(/[^\d]/g, '');
  // 천단위 콤마
  e.target.value = Number(val).toLocaleString('ko-KR');
  calculate();
});
```

### 3. 공제 계산 로직

```javascript
function calculate() {
  const gross = parseNumber(input.value) * 10000; // 만원 → 원
  const data = quizData; // loaded from data.json

  // 4대보험
  const pension = Math.min(gross * data.rates.nationalPension, data.rates.nationalPensionCap);
  const health = gross * data.rates.healthInsurance;
  const longterm = health * data.rates.longTermCare;
  const employ = gross * data.rates.employmentInsurance;

  // 소득세 (간이세액표 룩업)
  const incomeTax = lookupTax(gross / 10000, data.taxTable);
  const localTax = Math.floor(incomeTax * data.rates.localTaxRate);

  const totalDeduction = pension + health + longterm + employ + incomeTax + localTax;
  const netSalary = gross - totalDeduction;

  showResult(gross, netSalary, totalDeduction);
}

function lookupTax(salaryMan, table) {
  for (let i = table.length - 1; i >= 0; i--) {
    if (salaryMan >= table[i][0]) return table[i][1];
  }
  return 0;
}
```

### 4. 분위 비교

```javascript
function getPercentile(amount, salaryTable) {
  for (let i = salaryTable.length - 1; i >= 0; i--) {
    if (amount >= salaryTable[i].amount) {
      return salaryTable[i].percentile;
    }
  }
  return 100; // 하위
}
```

## 결과 표시 애니메이션 (숫자 카운트업)

```javascript
function animateNumber(el, target, duration = 1000) {
  const start = 0;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    // easeOutCubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.floor(start + (target - start) * eased);
    el.textContent = current.toLocaleString('ko-KR');
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}
```
