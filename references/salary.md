# salary - 2026 월급 계산기

> URL: https://salary.pearsoninsight.com
> GitHub: https://github.com/ganna40/salary

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 계산기형 바이럴 앱 |
| **한줄 설명** | 월급 입력 → 실수령액 계산 + 상위 몇% + LoL 티어 |
| **타겟** | 직장인 (카톡 공유 바이럴) |
| **테마** | 라이트 (Tailwind CDN) |
| **폰트** | Pretendard |

## 모듈 조합

```
BASE + DATA + SCREEN + CALC + GRADE + SHARE + GA + STYLE-LIGHT
```

## 특수 기능

| 기능 | 설명 |
|------|------|
| 4대보험 계산 | 국민연금, 건강보험, 장기요양, 고용보험 |
| 간이소득세 룩업 | taxTable 배열에서 구간 검색 |
| 부양가족 보정 | 1~4인 배수 적용 |
| 소득분위 비교 | 상위 몇% 표시 |
| LoL 티어 매핑 | Iron~Challenger |
| 추천 차량 | 월급 기준 차량 추천 |
| 미국 소득 비교 | 환율 적용 미국 계층 비교 |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| Kakao JS SDK 2.7.4 | 카톡 공유 |
| html2canvas 1.4.1 | 결과 스크린샷 |
| Tailwind CDN | CSS 유틸리티 |
| Google Analytics | 트래킹 |

## data.json 구조

```
salary-data.json
├── rates (4대보험 요율)
├── taxTable (간이세액표)
├── taxAdjustments (부양가족 보정)
├── salaryTable (소득분위)
├── lolTiers (LoL 티어 매핑)
├── cars (차량 데이터)
├── universityData (학벌별 소득)
└── usComparison (미국 비교)
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 salary 레퍼런스를 보고
"2026 연봉 계산기"를 만들어줘.
[CALC] + [GRADE] + [SHARE] 모듈 조합.
- 연봉 입력 → 월 실수령액
- 동일한 4대보험 계산 로직
- 소득 분위 비교 포함
- salary-data.json 구조 동일하게
```
