# tok-iq - 카카오톡 지능 분석기

> URL: tok-iq.pearsoninsight.com
> 로컬: C:\Users\ganna\Downloads\tok-iq

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 파일 분석기 (IQ 측정) |
| **한줄 설명** | 카카오톡 .txt 내보내기 파일을 업로드하면 웩슬러(WAIS) 기반 5대 인지지표로 톡IQ를 측정하는 바이럴 웹앱 |
| **타겟** | 카카오톡 사용자 (한국 인구 93%, ~4,700만 명) |
| **테마** | 다크 (뉴럴 네트워크 디자인) |
| **폰트** | Pretendard Variable (CDN) |

## 모듈 조합

```
BASE + SCREEN + GRADE + REVEAL + SHARE + CALC(숫자애니) + CAPTURE + SOUND + HAPTIC + STYLE-DARK + WebWorker + 웩슬러5지표엔진
```

## tok-wrapped와의 차이

| 항목 | tok-wrapped | tok-iq |
|------|-------------|--------|
| **측정 대상** | 대화 스타일 (MBTI, 캐릭터, 관계유형) | 인지 능력 (IQ) |
| **프레임워크** | 자체 룰기반 (4레이어 MBTI + 8계층 REL-TYPE) | 웩슬러(WAIS-V) 5대 인지지표 |
| **차트** | 8축 레이더 | 5축 펜타곤 |
| **점수 체계** | 캐릭터 유형 + MBTI 4축 | IQ 55~145 (웩슬러 척도) |
| **카드** | 13장 Wrapped 시퀀스 | 10장 (요약+5지표+펜타곤+IQ공개+랭킹+공유) |
| **파서** | 공유 (동일 카카오톡 정규식) | 공유 (동일 카카오톡 정규식) |

## 특수 기능

| 기능 | 설명 |
|------|------|
| **카카오톡 .txt 파싱** | 모바일+PC 내보내기 포맷 정규식 파싱, 멀티라인 처리, UTF-8 BOM 제거, 오전/오후→24시 변환 |
| **Web Worker 파싱** | 대용량 파일 메인 스레드 블로킹 방지, 프로그레스 보고 |
| **웩슬러 5대 인지지표** | VCI(언어이해), FRI(유동추론), WMI(작업기억), PSI(처리속도), VSI(시공간) — WAIS-V 구조 |
| **그룹 적응형 스코어링** | S() 지수감쇠 + R() z-score+tanh — 그룹 내 상대적 위치 기반 점수 산출 |
| **웩슬러 척도 변환** | raw 0~100 → Index 55~145 (mean≈100, SD≈15) → FSIQ 균등평균 |
| **인지 사전 6종** | FORMAL_WORDS(격식체), ADVANCED_VOCAB(고급어휘), CONDITIONAL_WORDS(조건추론), PROBLEM_SOLVE(문제해결), CONTEXT_REF(맥락참조), 기존 언어깊이 사전 |
| **5축 펜타곤 차트** | SVG 기반 5축, rawScores(0~100)로 도형, 지표(55~145)로 라벨 |
| **10장 카드 시퀀스** | 요약 → VCI → FRI → WMI → PSI → VSI → 펜타곤 → IQ 공개 → 랭킹 → 공유 |
| **웩슬러 분류 6단계** | 최우수(130+), 우수(120+), 평균상(110+), 평균(100+), 평균하(90+), 경계(<90) |
| **효과음 + 햅틱** | Web Audio OscillatorNode + Vibration API |
| **100% 정적** | 백엔드 없음, 서버 비용 ₩0, 대화 데이터 브라우저 밖으로 안 나감 |
| **이미지 저장** | html2canvas로 결과 카드 PNG 저장 |
| **참가자 자동 감지** | 1:1은 첫 번째 참가자, 그룹은 선택 UI |
| **OG 이미지** | Pillow gen_og.py (1200x630) 뉴럴 네트워크 디자인 |

## 핵심 기술

| 기술 | 용도 |
|------|------|
| Web Worker | 대용량 .txt 파싱 (메인 스레드 보호) |
| 정규식 파서 | 카카오톡 모바일/PC 내보내기 포맷 파싱 |
| 웩슬러 5지표 엔진 | VCI/FRI/WMI/PSI/VSI 스코어링 (그룹 적응형) |
| 인지 사전 시스템 | 격식체/고급어휘/조건추론/문제해결/맥락참조 사전 매칭 |
| SVG 펜타곤 차트 | 5축 레이더 (삼각함수 꼭짓점 계산) |
| html2canvas | 결과 카드 스크린샷 저장 |
| Web Audio API | OscillatorNode 효과음 (외부 파일 불필요) |
| Vibration API | 모바일 햅틱 피드백 |
| Pretendard Variable | 한글 웹폰트 (CDN) |
| Pillow (PIL) | OG 썸네일 생성 (1200x630) |

## 파일 구조

```
tok-iq/
├── index.html     # HTML + 인라인 CSS (다크 뉴럴 테마)
├── app.js         # 펜타곤 차트 + 10장 카드 렌더링 + 정밀분석 + 공유
├── worker.js      # KakaoTalk .txt 파서 + 통계 추출 + 웩슬러 5지표 엔진
├── gen_og.py      # Pillow OG 이미지 생성 (1200x630)
└── og.png         # 생성된 OG 이미지
```

## 웩슬러 5대 인지지표 구조

### WAIS-V 기반 5 Indices

| 약어 | 지표 | 아이콘 | 측정 신호 |
|------|------|--------|----------|
| **VCI** | 언어이해 | 📝 | 어휘 다양성, 격식체(따라서/그러므로), 고급어휘(함의/맥락/관점), 긴 단어, 문장 복잡도, 추상어, 비속어(-) |
| **FRI** | 유동추론 | 🧩 | 인과표현, 조건추론(만약/가정하면), 문제해결(해결/방법/대안), 분석표현, 수량추론, 분류/비교, 링크공유 |
| **WMI** | 작업기억 | 🧠 | 맥락참조(아까/그때/전에), 다중절 문장, 문장 복잡도, 평균 문장 길이, 주제 주도, 연결어 |
| **PSI** | 처리속도 | ⚡ | 응답속도(역), 일평균 메시지, 표현효율(단어/메시지), 단답(-), 총 볼륨 |
| **VSI** | 시공간 | 🗺️ | 미디어 공유, 공간묘사, 장소언급, 이모티콘, 구체적 디테일, 이모지 |

### 그룹 적응형 스코어링 (v3)

```javascript
// S(): 절대적 비율 기반 — 지수감쇠, 20% 바닥
function S(val, groupAvg, maxPts) {
  const r = val / Math.max(groupAvg, 0.0001);
  const mapped = 1 - Math.exp(-r * 1.2);
  return maxPts * (0.2 + mapped * 0.8);
}

// R(): 상대적 위치 기반 — z-score + tanh 정규화
function R(val, groupAvg, groupStd, maxPts) {
  const z = (val - groupAvg) / groupStd;
  return maxPts * (Math.tanh(z * 0.6) + 1) / 2;
}

// S_inv(), R_inv(): 역방향 (낮을수록 좋은 지표용)
```

### 웩슬러 척도 변환

```javascript
// raw 0~100 → Index 55~145
indices[key] = clamp(55, 145, 40 + raw[key] * 0.95);

// FSIQ = 5개 지표 균등 평균
const fsiq = (VCI + FRI + WMI + PSI + VSI) / 5;
```

### 인지 사전 (웩슬러 전용 6종)

```javascript
// VCI: 격식체 + 고급어휘
const FORMAL_WORDS = ['따라서','그러므로','더불어','뿐만아니라','비록','그럼에도','한편','결론적으로','요컨대','즉',...];
const ADVANCED_VOCAB = ['함의','맥락','관점','측면','양상','현상','개념','원리','구조','체계','범주',...];

// FRI: 조건추론 + 문제해결
const CONDITIONAL_WORDS = ['만약','가정하면','그렇다면','라면','경우에','전제로','조건이','상황에서',...];
const PROBLEM_SOLVE = ['해결','방법','대안','시도','접근','전략','방안','대처','해법',...];

// WMI: 맥락 참조
const CONTEXT_REF = ['아까','그때','전에','방금','좀전에','이전에','위에서','말했듯이','했잖아',...];

// 기존: T_WORDS, F_WORDS, E_WORDS, I_WORDS, S_WORDS, N_WORDS, J_WORDS, P_WORDS (tok-wrapped 재활용)
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 tok-iq 레퍼런스를 보고
"___" 파일 분석기를 만들어줘.
BASE + SCREEN + GRADE + REVEAL + SHARE + STYLE-DARK + WebWorker + 인지측정엔진 조합.
파일을 브라우저에서 파싱하고 카드 시퀀스로 결과를 보여주는 형태.
웩슬러 5지표 스코어링(S/R 그룹 적응형 + 인지 사전 매칭) 구조를 참고.
펜타곤 차트가 필요하면 SVG 5축 구조를 참고.
```
