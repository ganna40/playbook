# [HAPTIC] 진동 피드백 — Vibration API

> `navigator.vibrate()`로 모바일 햅틱 피드백.
> 코드 1줄. 지원 안 되면 무시됨 (graceful degradation).

## 핵심 로직

```javascript
const HAP = {
  tap()    { navigator.vibrate?.([30]); },           // 가벼운 터치
  select() { navigator.vibrate?.([50]); },           // 선택 확정
  swipe()  { navigator.vibrate?.([40, 30, 40]); },   // 스와이프 (더블 펄스)
  result() { navigator.vibrate?.([100, 50, 100, 50, 200]); }, // 결과 공개 (팡파르)
};
```

## 사용 예시

```javascript
// 버튼 클릭 시
HAP.select();

// 스와이프 확정 시
HAP.swipe();

// 결과 공개 시
HAP.result();
```

## 진동 패턴 가이드

| 이름 | 패턴 (ms) | 체감 | 용도 |
|------|-----------|------|------|
| tap | [30] | 짧은 톡 | 드래그 이동, 순위 변경 |
| select | [50] | 확정 느낌 | 버튼 선택, 슬라이더 확인 |
| swipe | [40, 30, 40] | 두번 톡톡 | 스와이프 확정 |
| result | [100, 50, 100, 50, 200] | 팡파르 | 최종 결과 공개 |

> 배열 형식: `[진동ms, 휴지ms, 진동ms, ...]`

## 삽질 방지

- **Optional chaining `?.` 필수** — iOS Safari는 `navigator.vibrate` 미지원
- **너무 긴 진동 금지** — 200ms 이상은 불쾌감
- **항상 음소거와 연동** — 소리 끄면 진동도 끄는 게 자연스러움
- **데스크탑에서는 무시됨** — 별도 처리 불필요
