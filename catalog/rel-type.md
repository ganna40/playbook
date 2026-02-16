# REL-TYPE 관계 유형 추정 엔진

> 채팅 메시지를 분석해서 대화 상대와의 관계(연인/썸/친구/가족/직장)를 추정.
> 메시지 1회 순회 O(n)로 8개 신호를 동시 수집, 가중합산으로 5종 유형 판정.
> 의존: 없음 (독립 모듈, 메시지 배열만 있으면 동작)

## 언제 쓰나

- 카카오톡/라인/텔레그램 등 채팅 로그 분석기
- 대화 스타일 기반 관계 추정
- 100% 브라우저 로컬 처리 (서버 불필요)

## 5종 유형 (1:1)

| 코드 | 한글 | 핵심 구분자 |
|------|------|------------|
| LOVER | 연인 | 로맨틱 호칭 + 하트이모지 + 굿모닝/나잇 루틴 + 친밀도 L5 |
| FLIRT | 썸 | 존댓말 소멸 추이 + "뭐해" 폭격 + L4 있지만 L5 없음 |
| FRIEND | 친구 | 비속어 허용 + 불규칙 패턴 + 로맨틱 신호 부재 |
| FAMILY | 가족 | 가족 호칭 + 존댓말 비대칭 + 식사/안전 체크 루틴 |
| WORK | 직장 | 양방향 존댓말 + 업무 키워드 + 9-18시 시간대 집중 |

## 3종 유형 (그룹)

| 코드 | 한글 | 핵심 구분자 |
|------|------|------------|
| FRIEND | 친구 모임 | 반말 + 비속어 + 심야대화 |
| FAMILY | 가족방 | 가족 호칭 + 식사체크 + 존댓말 혼재 |
| WORK | 직장 단톡 | 님 호칭 + 존댓말 높음 + 9-18시 집중 |

## 8계층 신호 (1:1)

| 계층 | 수집 대상 | 판별 원리 |
|------|----------|----------|
| L1 존대법 | 메시지 끝 `/(요\|니다\|세요\|시오)/` | 양쪽 낮음=연인/친구, 양쪽 높음=직장, 비대칭=가족 |
| L2 호칭 | 문두 12자 `startsWith` + 하트이모지 주당빈도 | 자기야=연인, 엄마=가족, 님=직장, 야=친구 |
| L3 의례 | 굿모닝/굿나잇/식사/안전/뭐해/업무어 주당빈도 | 모닝+나잇=연인, 뭐해폭격=썸, 식사=가족 |
| L4 친밀도 | 사랑해(L5)>보고싶(L4)>힘들었어(L3)+신체+질투 | **존재 신호**: 1번=0.5점 기본 + 주당빈도 보너스 |
| L5 시간대 | 24h 분포 vs 유형별 이상 프로필 코사인 유사도 | 9-18시=직장, 전시간대+심야=연인 |
| L6 역학 | 메시지량/길이 균형, 2시간+ 장시간 세션 비율 | 균형+장시간=연인, 불균형=썸 |
| L7 언어 | 비속어/돈 키워드/애정디스(바보야~) | 비속어=친구, 돈=가족, 바보야=연인 |
| L8 진화 | 대화 3등분 → 존댓말/친밀도 변화 추적 | 존댓말↓+친밀도↑=썸→연인 |

## 필요 상수

```javascript
// === 정규식 ===
const REL_HONORIFIC = /(요|니다|세요|시오)[\s.!?~…ㅋㅎ]*$/;
const REL_MORNING = /(좋은아침|굿모닝|일어났|기상|모닝|좋은 아침)/;
const REL_NIGHT = /(잘자|굿나잇|좋은꿈|자러간|잘게|꿈에서|푹자|좋은 꿈)/;
const REL_MEAL = /(밥먹었|밥먹어|점심먹|저녁먹|아침먹|밥은|식사|밥 먹)/;
const REL_SAFETY = /(잘들어갔|도착했|집도착|잘갔|무사히|조심히|잘 들어)/;
const REL_WHATCHA = /(뭐해|모해|머해|뭐하는|뭐하고|뭐 해)/;
const REL_WORK_KW = /(미팅|회의|보고서|프로젝트|일정|출근|퇴근|야근|업무|거래처|클라이언트|마감)/;
const REL_PROFANITY = /(시발|씨발|존나|좆|개새|병신|지랄|ㅅㅂ|ㅈㄴ)/;
const REL_MONEY_KW = /(용돈|이체|입금|보내줘|만원|천원|돈좀|카드값|생활비|월급)/;
const REL_AFFECT_DISS = /(바보|멍청이|바보야|멍충|빠가|귀여운바보|못난이|이 바보)/;

// === 단어 사전 ===
const REL_ROMANTIC = ['자기야','여보','아가야','내사랑','달링','허니','애기야','내꺼야','여보야'];
const REL_FAMILY_ADDR = ['엄마','아빠','형아','누나','언니','할머니','할아버지','아들','딸아'];
const REL_WORK_ADDR = ['님','과장님','대리님','부장님','사장님','팀장님','선생님','차장님','실장님','이사님','매니저'];
const REL_FRIEND_ADDR = ['야 ','임마','이놈','이년','씨 '];
const REL_HEARTS = ['❤','💕','😍','🥰','💗','💖','💓','💘','💝','💞','🫶','♥','💌','😘'];
const REL_L5_INTIMATE = ['사랑해','사랑한다','결혼하자','결혼','내꺼','내거','평생','영원히','사랑행'];
const REL_L4_INTIMATE = ['보고싶','그리워','소중해','좋아해','좋아한다','안고싶','보고파','그립다'];
const REL_L3_INTIMATE = ['힘들었어','행복해','슬퍼','기뻐','외로워','행복하다','기쁘다'];
const REL_BODY = ['뽀뽀','키스','안아줘','껴안','스킨십','잠자리','안겨'];
const REL_JEALOUS = ['누구랑','왜안읽','왜씹','읽씹','누구만나','바람','질투'];

// === 가중치 (L1~L8) ===
const REL_WEIGHTS = {
  LOVER:  [5,  20, 15, 20, 10, 10, 10, 10],
  FLIRT:  [15, 10, 20, 15, 10, 15,  5, 10],
  FRIEND: [10, 15,  5, 10, 15, 10, 25, 10],
  FAMILY: [20, 25, 20, 10, 10,  5,  5,  5],
  WORK:   [25, 20, 15,  5, 20,  5,  5,  5],
};
const REL_LABELS = { LOVER:'연인', FLIRT:'썸', FRIEND:'친구', FAMILY:'가족', WORK:'직장' };

// === 24h 이상 프로필 (코사인 유사도 비교용) ===
const REL_TIME_PROFILES = {
  LOVER:  [3,2,2,1,0,0,1,3,4,5,5,6,6,6,6,6,6,6,7,7,8,8,6,4],
  FLIRT:  [1,0,0,0,0,0,0,1,2,4,4,5,5,5,4,4,4,5,6,7,8,7,4,2],
  FRIEND: [1,0,0,0,0,0,0,1,2,3,4,5,5,5,5,5,5,5,6,7,7,6,3,2],
  FAMILY: [0,0,0,0,0,0,1,3,5,4,3,4,7,4,3,3,3,4,7,6,4,2,1,0],
  WORK:   [0,0,0,0,0,0,0,1,3,8,8,7,5,6,8,8,7,6,3,1,0,0,0,0],
};
```

## 핵심 코드 (1:1)

```javascript
/**
 * 관계 유형 추정 (1:1 대화)
 * @param {Array} messages - [{ sender, text, hour, weekday, date }]
 * @param {Array} participants - ['A', 'B']
 * @param {Array} conversations - [{ start, end }] (60분 갭 기준 대화 분리)
 * @param {number} totalDays - 대화 전체 일수
 * @returns {{ type, label, confidence, scores, signals, evolution }}
 */
function computeRelationship(messages, participants, conversations, totalDays) {
  if (participants.length < 2 || messages.length === 0) return null;

  const A = participants[0], B = participants[1];
  const totalWeeks = Math.max(1, totalDays / 7);
  const msgLen = messages.length;
  const phaseSize = Math.ceil(msgLen / 3);

  // --- 누적 변수 (8계층 동시 수집) ---
  const hon = { A: 0, B: 0, totalA: 0, totalB: 0 };
  const honPhase = [[0,0],[0,0],[0,0]];
  const phaseTotal = [[0,0],[0,0],[0,0]];
  const addr = { romantic: 0, family: 0, work: 0, friend: 0 };
  let heartCount = 0;
  const ritual = { morning: 0, night: 0, meal: 0, safety: 0, whatcha: 0, workKw: 0 };
  const intim = { L5: 0, L4: 0, L3: 0, body: 0, jealous: 0 };
  const intimPhase = [0, 0, 0];
  const hourlyAll = new Array(24).fill(0);
  let weekdayCount = 0, weekendCount = 0, lateNightCount = 0;
  const lenA = [], lenB = [];
  let profanity = 0, moneyHits = 0, affectDiss = 0;

  // --- 메시지 1회 순회 O(n) ---
  for (let i = 0; i < msgLen; i++) {
    const m = messages[i];
    const t = m.text;
    const isA = m.sender === A;
    const phase = Math.min(2, Math.floor(i / phaseSize));
    const h = m.hour;
    const wd = m.weekday;

    // L1: 존대법 비대칭
    if (isA) { hon.totalA++; phaseTotal[phase][0]++;
      if (REL_HONORIFIC.test(t)) { hon.A++; honPhase[phase][0]++; }
    } else { hon.totalB++; phaseTotal[phase][1]++;
      if (REL_HONORIFIC.test(t)) { hon.B++; honPhase[phase][1]++; }
    }

    // L2: 호칭 (문두 12자, startsWith로 오탐 방지)
    const head = t.substring(0, 12);
    if (REL_ROMANTIC.some(w => head.startsWith(w) || head.startsWith(' ' + w))) addr.romantic++;
    if (REL_FAMILY_ADDR.some(w => head.includes(w))) addr.family++;
    if (REL_WORK_ADDR.some(w => head.includes(w))) addr.work++;
    if (REL_FRIEND_ADDR.some(w => head.includes(w))) addr.friend++;
    if (REL_HEARTS.some(e => t.includes(e))) heartCount++;

    // L3: 대화 의례 패턴 (시간대 조건부)
    if (h >= 6 && h <= 9 && REL_MORNING.test(t)) ritual.morning++;
    if ((h >= 22 || h <= 2) && REL_NIGHT.test(t)) ritual.night++;
    if (REL_MEAL.test(t)) ritual.meal++;
    if (REL_SAFETY.test(t)) ritual.safety++;
    if (REL_WHATCHA.test(t)) ritual.whatcha++;
    if (REL_WORK_KW.test(t)) ritual.workKw++;

    // L4: 친밀도 계층
    let pIntim = 0;
    if (REL_L5_INTIMATE.some(w => t.includes(w))) { intim.L5++; pIntim += 5; }
    if (REL_L4_INTIMATE.some(w => t.includes(w))) { intim.L4++; pIntim += 4; }
    if (REL_L3_INTIMATE.some(w => t.includes(w))) { intim.L3++; pIntim += 3; }
    if (REL_BODY.some(w => t.includes(w))) { intim.body++; pIntim += 5; }
    if (REL_JEALOUS.some(w => t.includes(w))) { intim.jealous++; pIntim += 3; }
    intimPhase[phase] += pIntim;

    // L5: 시간대 지문
    hourlyAll[h]++;
    if (wd === 0 || wd === 6) weekendCount++; else weekdayCount++;
    if (h >= 0 && h <= 4) lateNightCount++;

    // L6: 메시지 길이 수집
    if (isA) lenA.push(t.length); else lenB.push(t.length);

    // L7: 언어 허용 스펙트럼
    if (REL_PROFANITY.test(t)) profanity++;
    if (REL_MONEY_KW.test(t)) moneyHits++;
    if (REL_AFFECT_DISS.test(t)) affectDiss++;
  }

  // === 8계층 스코어 산출 (각 0~1) ===
  const layerScores = { LOVER: [], FLIRT: [], FRIEND: [], FAMILY: [], WORK: [] };

  // L1: 존대법 비대칭
  const honRateA = hon.totalA > 0 ? hon.A / hon.totalA : 0;
  const honRateB = hon.totalB > 0 ? hon.B / hon.totalB : 0;
  const honAvg = (honRateA + honRateB) / 2;
  const honAsym = Math.abs(honRateA - honRateB);
  const honDecay = (() => {
    const p0A = phaseTotal[0][0] > 0 ? honPhase[0][0] / phaseTotal[0][0] : 0;
    const p2A = phaseTotal[2][0] > 0 ? honPhase[2][0] / phaseTotal[2][0] : 0;
    const p0B = phaseTotal[0][1] > 0 ? honPhase[0][1] / phaseTotal[0][1] : 0;
    const p2B = phaseTotal[2][1] > 0 ? honPhase[2][1] / phaseTotal[2][1] : 0;
    return ((p0A - p2A) + (p0B - p2B)) / 2;
  })();
  layerScores.LOVER.push(1 - honAvg);
  layerScores.FLIRT.push(Math.min(1, Math.max(0, honDecay) * 3 + 0.3));
  layerScores.FRIEND.push(1 - honAvg);
  layerScores.FAMILY.push(Math.min(1, honAsym * 2));
  layerScores.WORK.push(honAvg);

  // L2: 호칭 (하트는 주당 빈도 + 존재 보너스)
  const addrPer100 = Math.max(1, msgLen / 100);
  const heartsPerWeek = heartCount / totalWeeks;
  const romScore = Math.min(1,
    addr.romantic / addrPer100 * 0.2
    + (heartCount > 0 ? 0.3 : 0)
    + Math.min(1, heartsPerWeek / 2) * 0.5);
  layerScores.LOVER.push(romScore);
  layerScores.FLIRT.push(romScore * 0.5);
  layerScores.FRIEND.push(Math.min(1, addr.friend / addrPer100));
  layerScores.FAMILY.push(Math.min(1, addr.family / addrPer100));
  layerScores.WORK.push(Math.min(1, addr.work / addrPer100));

  // L3: 의례 (인티머시 게이트: L4 없으면 LOVER L3 감쇠)
  const mPW = ritual.morning / totalWeeks;
  const nPW = ritual.night / totalWeeks;
  const safePW = ritual.safety / totalWeeks;
  const ritualRaw = Math.min(1, (mPW + nPW) / 5 * 0.6 + safePW / 3 * 0.4);
  const hasIntimacy = (intim.L5 + intim.L4 + intim.body) > 0;
  layerScores.LOVER.push(ritualRaw * (hasIntimacy ? 1 : 0.3));
  layerScores.FLIRT.push(Math.min(1, ritual.whatcha / totalWeeks / 5));
  layerScores.FRIEND.push(Math.min(1, ritual.whatcha / totalWeeks / 8 * 0.5));
  layerScores.FAMILY.push(Math.min(1, (ritual.meal / totalWeeks + safePW) / 5));
  layerScores.WORK.push(Math.min(1, ritual.workKw / totalWeeks / 5));

  // L4: 친밀도 (존재 신호 — 1번만 있어도 기본점)
  const ipw = (k) => k / totalWeeks;
  const loverL4 = Math.min(1,
    (intim.L5 > 0 ? 0.5 : 0) + ipw(intim.L5) * 2
    + (intim.body > 0 ? 0.2 : 0) + ipw(intim.body)
    + ipw(intim.jealous) * 0.5);
  layerScores.LOVER.push(loverL4);
  layerScores.FLIRT.push(
    Math.min(1, (intim.L4 > 0 ? 0.3 : 0) + ipw(intim.L4) * 0.5)
    * (intim.L5 === 0 ? 1 : 0.3));
  layerScores.FRIEND.push(
    Math.min(1, ipw(intim.L3) / 3)
    * (intim.L5 === 0 && intim.L4 < 3 ? 1 : 0.2));
  layerScores.FAMILY.push(Math.min(1, ipw(intim.L4 + intim.L3) / 4));
  layerScores.WORK.push(
    intim.L5 + intim.L4 + intim.body + intim.jealous === 0 ? 0.5 : 0.05);

  // L5: 시간대 지문 (코사인 유사도)
  function cosineSim(a, b) {
    let dot = 0, magA = 0, magB = 0;
    for (let j = 0; j < a.length; j++) {
      dot += a[j] * b[j]; magA += a[j] * a[j]; magB += b[j] * b[j];
    }
    return (magA > 0 && magB > 0) ? dot / (Math.sqrt(magA) * Math.sqrt(magB)) : 0;
  }
  const weekendRatio = (weekdayCount + weekendCount) > 0
    ? weekendCount / (weekdayCount + weekendCount) : 0;
  const lateNightRatio = msgLen > 0 ? lateNightCount / msgLen : 0;
  for (const tp of ['LOVER','FLIRT','FRIEND','FAMILY','WORK']) {
    let s = cosineSim(hourlyAll, REL_TIME_PROFILES[tp]);
    if (tp === 'LOVER')
      s = s * 0.7 + Math.min(1, lateNightRatio * 10) * 0.15 + Math.min(1, weekendRatio * 3) * 0.15;
    else if (tp === 'WORK')
      s = s * 0.7 + Math.min(1, (1 - weekendRatio)) * 0.15 + Math.max(0, 1 - lateNightRatio * 10) * 0.15;
    else if (tp === 'FAMILY')
      s = s * 0.8 + Math.max(0, 1 - lateNightRatio * 10) * 0.2;
    layerScores[tp].push(Math.min(1, Math.max(0, s)));
  }

  // L6: 상호작용 역학
  const avgLenA = lenA.length > 0 ? lenA.reduce((a, b) => a + b, 0) / lenA.length : 0;
  const avgLenB = lenB.length > 0 ? lenB.reduce((a, b) => a + b, 0) / lenB.length : 0;
  const msgBalance = Math.min(lenA.length, lenB.length)
    / Math.max(1, Math.max(lenA.length, lenB.length));
  const lenBalance = Math.min(avgLenA, avgLenB)
    / Math.max(1, Math.max(avgLenA, avgLenB));
  let longSessions = 0;
  for (const conv of conversations) {
    if ((messages[conv.end].date - messages[conv.start].date) / (1000 * 60) >= 120)
      longSessions++;
  }
  const longSessionPct = conversations.length > 0 ? longSessions / conversations.length : 0;
  const sessionsPerDay = conversations.length / Math.max(1, totalDays);
  layerScores.LOVER.push(Math.min(1,
    msgBalance * 0.3 + lenBalance * 0.2 + longSessionPct * 0.3
    + Math.min(1, sessionsPerDay / 5) * 0.2));
  layerScores.FLIRT.push(Math.min(1,
    (1 - msgBalance) * 0.5 + Math.min(1, sessionsPerDay / 3) * 0.5));
  layerScores.FRIEND.push(Math.min(1,
    msgBalance * 0.4 + (1 - longSessionPct) * 0.3
    + Math.min(1, sessionsPerDay / 3) * 0.3));
  layerScores.FAMILY.push(Math.min(1,
    (1 - longSessionPct) * 0.5 + msgBalance * 0.5));
  layerScores.WORK.push(Math.min(1,
    (1 - longSessionPct) * 0.6 + lenBalance * 0.4));

  // L7: 언어 허용 스펙트럼
  const profRate = msgLen > 0 ? profanity / msgLen : 0;
  const dissRate = msgLen > 0 ? affectDiss / msgLen : 0;
  layerScores.LOVER.push(Math.min(1,
    dissRate * 100 * 0.7 + Math.max(0, 1 - profRate * 50) * 0.3));
  layerScores.FLIRT.push(Math.min(1,
    Math.max(0, 1 - profRate * 50) * 0.7 + dissRate * 50 * 0.3));
  layerScores.FRIEND.push(Math.min(1, profRate * 40 + 0.15));
  layerScores.FAMILY.push(Math.min(1, moneyHits / msgLen * 50));
  layerScores.WORK.push(profRate === 0 && dissRate === 0 ? 0.3 : 0.05);

  // L8: 관계 진화 감지
  const phaseTotalAll = [
    phaseTotal[0][0] + phaseTotal[0][1],
    phaseTotal[1][0] + phaseTotal[1][1],
    phaseTotal[2][0] + phaseTotal[2][1],
  ];
  const intimP0 = phaseTotalAll[0] > 0 ? intimPhase[0] / phaseTotalAll[0] : 0;
  const intimP2 = phaseTotalAll[2] > 0 ? intimPhase[2] / phaseTotalAll[2] : 0;
  const intimChange = intimP2 - intimP0;
  const intimTrend = intimChange > 0.05 ? 'increasing' : intimChange < -0.05 ? 'decreasing' : 'stable';
  const honTrend = honDecay > 0.05 ? 'decreasing' : honDecay < -0.05 ? 'increasing' : 'stable';
  layerScores.LOVER.push(Math.min(1, intimP2 * 2));
  layerScores.FLIRT.push(Math.min(1, Math.max(0, intimChange) * 5 + Math.max(0, honDecay) * 3));
  layerScores.FRIEND.push(intimTrend === 'stable' ? 0.7 : 0.3);
  layerScores.FAMILY.push(intimTrend === 'stable' ? 0.6 : 0.3);
  layerScores.WORK.push(intimTrend === 'stable' && honTrend === 'stable' ? 0.4 : 0.1);

  // === 교차 감쇠 (모순 방지) ===
  const romanticEvidence = intim.L5 + intim.L4 + intim.body + addr.romantic;
  if (romanticEvidence === 0) {
    for (let j = 0; j < 8; j++) layerScores.LOVER[j] *= 0.6;
  }
  if (romanticEvidence > 2) {
    for (let j = 0; j < 8; j++) layerScores.WORK[j] *= 0.4;
  }

  // === 가중 합산 → 0~100 ===
  const finalScores = {};
  let bestType = 'FRIEND', bestScore = -1;
  for (const tp of ['LOVER','FLIRT','FRIEND','FAMILY','WORK']) {
    let total = 0;
    for (let j = 0; j < 8; j++) total += (layerScores[tp][j] || 0) * REL_WEIGHTS[tp][j];
    finalScores[tp] = Math.round(Math.min(100, Math.max(0, total)));
    if (finalScores[tp] > bestScore) { bestScore = finalScores[tp]; bestType = tp; }
  }

  return {
    type: bestType,
    label: REL_LABELS[bestType],
    confidence: bestScore,
    scores: finalScores,
    labels: { ...REL_LABELS },
    signals: { /* L1~L7 세부 데이터 */ },
    evolution: { intimacyTrend: intimTrend, honorificTrend: honTrend },
  };
}
```

## 주의사항

- **호칭 오탐 방지**: 로맨틱 호칭은 `startsWith` 사용 (교촌 "허니"콤보 같은 오탐 차단)
- **"자기" 제외**: "자기 전에 잘게"(수면 전) vs "자기야"(호칭) — 다의어라 "자기야"만 포함
- **존재 신호**: "사랑해"는 빈도보다 존재 여부가 중요 (1회만 있어도 LOVER L4에 0.5점)
- **주당 빈도 정규화**: 메시지 수 대신 주(week) 단위로 정규화해야 대화량 많은 관계에서 신호 희석 안됨
- **WORK 과대평가 방지**: L7(깨끗한 언어 0.3), L8(안정적 변화 0.4) 디폴트를 낮게 설정
- **인티머시 게이트**: 굿모닝/굿나잇만으로 LOVER 과대평가 방지 — L4 신호가 있어야 L3 풀점수
- **교차 감쇠**: 로맨틱 신호 0 → LOVER ×0.6 / 로맨틱 신호 3+ → WORK ×0.4

## 사용 예시

```javascript
// 메시지 파싱 후
const result = computeRelationship(messages, participants, conversations, totalDays);
// result = { type: 'LOVER', label: '연인', confidence: 78, scores: {...}, ... }

// 그룹채팅은 별도 함수
const groupResult = computeGroupRelationship(messages, participants, conversations, totalDays);
// groupResult = { type: 'FRIEND', label: '친구 모임', confidence: 58, scores: {...}, ... }
```

## 가중치 표

```
             L1존대 L2호칭 L3의례 L4친밀 L5시간 L6역학 L7언어 L8진화
LOVER:         5     20     15     20     10     10     10     10
FLIRT:        15     10     20     15     10     15      5     10
FRIEND:       10     15      5     10     15     10     25     10
FAMILY:       20     25     20     10     10      5      5      5
WORK:         25     20     15      5     20      5      5      5
```

## 그룹채팅 가중치 (5개 신호)

```
              S1존대  S2호칭  S3의례  S4시간  S5언어
FRIEND:        10     20     10     20     40
FAMILY:        25     30     25     10     10
WORK:          30     25     15     25      5
```
