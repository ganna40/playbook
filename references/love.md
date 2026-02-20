# love - 나의 연애 유형 테스트

> URL: https://love.pearsoninsight.com
> GitHub: https://github.com/ganna40/love-test

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 혼합형 다차원 테스트 |
| **한줄 설명** | 15문항 (스와이프/슬라이더/랭킹/선택) → 5축 레이더 + 5유형 판정 |
| **타겟** | 20-30대 (카톡/인스타 바이럴) |
| **테마** | 다크 (핑크+퍼플 악센트) |
| **폰트** | Pretendard |

## 모듈 조합

```
BASE + SCREEN + QUIZ + GRADE + RADAR + TIMER + REVEAL + URL-ENCODE + SHARE + CALC + STYLE-DARK
+ SWIPE + CAPTURE + SOUND + HAPTIC + SPECTRUM + DRAG-RANK  ← 신규 6개
```

## 신규 모듈 (이 프로젝트에서 최초 도입)

| 모듈 | 기술 | 설명 |
|------|------|------|
| **SWIPE** | Touch Events | 틴더식 좌/우 스와이프로 동의/비동의 답변 |
| **CAPTURE** | html2canvas | 결과 화면을 PNG 이미지로 캡처+다운로드 |
| **SOUND** | Web Audio API | OscillatorNode로 효과음 생성 (외부 파일 불필요) |
| **HAPTIC** | Vibration API | 선택/스와이프/결과 시 모바일 진동 피드백 |
| **SPECTRUM** | input[range] | 슬라이더로 0~100 연속 스펙트럼 답변 |
| **DRAG-RANK** | Touch + Drag | 항목을 드래그해서 순위 매기기 |

## 질문 타입 혼합

```
15문항 = 5×SWIPE + 4×SPECTRUM + 1×RANK + 5×CHOICE
```

| 타입 | 문항수 | UX | 점수 방식 |
|------|--------|-----|-----------|
| SWIPE | 5 | 카드 좌/우 스와이프 | agree/disagree 각각 별도 점수 |
| SPECTRUM | 4 | 슬라이더 0~100 | leftScores↔rightScores 보간 |
| RANK | 1 | 4항목 드래그 순위 | 1위×4, 2위×3, 3위×2, 4위×1 가중 |
| CHOICE | 5 | 3지선다 버튼 | 선택지별 고정 점수 |

## 5축 분석

| 축 | 이름 | 설명 |
|----|------|------|
| rom | 로맨스 | 표현력, 이벤트, 감동 추구 |
| ind | 독립성 | 개인 공간, 쿨한 관계, 자기주관 |
| adv | 모험 | 즉흥성, 새 경험, 도전 |
| stb | 안정 | 편안함, 신뢰, 장기적 계획 |
| emo | 감성 | 공감, 깊은 대화, 감수성 |

## 5유형 결과

| 유형 | 지배축 | 아이콘 |
|------|--------|--------|
| 다정한 로맨티스트 | rom | 💕 |
| 쿨한 독립주의자 | ind | 🌿 |
| 열정적 모험가 | adv | 🔥 |
| 따뜻한 안정주의자 | stb | 🏡 |
| 깊은 감성주의자 | emo | 🎭 |

## AI에게 비슷한 거 만들게 하려면

```
playbook의 love 레퍼런스를 보고
"리더십 유형 검사"를 만들어줘.
[SWIPE] + [SPECTRUM] + [DRAG-RANK] + [CAPTURE] + [SOUND] + [HAPTIC]
- 15문항 혼합형 (스와이프 5 + 슬라이더 4 + 랭킹 1 + 선택 5)
- 5축: 소통, 결단, 공감, 전략, 실행
- 레이더 차트 + 이미지 캡처 + 효과음
```
