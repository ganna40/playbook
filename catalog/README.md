# 모듈 카탈로그

> 레고 블록처럼 조합해서 앱을 만드는 빌딩블록.
> 각 모듈은 독립적이며, 필요한 것만 골라서 조합.

## 한눈에 보기

| 모듈 | 용도 | 의존성 |
|------|------|--------|
| [BASE](base.md) | SPA 기본 골격 (HTML + 모바일) | 없음 |
| [DATA](data.md) | JSON 데이터 분리 패턴 | 없음 |
| [SCREEN](screen.md) | 화면 전환 (인트로→진행→결과) | BASE |
| [QUIZ](quiz.md) | 퀴즈/설문 엔진 | BASE, DATA, SCREEN |
| [CALC](calc.md) | 계산기 엔진 | BASE, DATA, SCREEN |
| [GRADE](grade.md) | 등급/티어 시스템 | DATA |
| [RADAR](radar.md) | 레이더 차트 (Canvas) | 없음 |
| [KAKAO](kakao.md) | 카카오톡 공유 | 없음 |
| [OG](og.md) | Open Graph 메타태그 | 없음 |
| [SHARE](share.md) | 통합 공유 (카카오+URL+스크린샷) | KAKAO, OG |
| [GA](ga.md) | Google Analytics 트래킹 | 없음 |
| [TIMER](timer.md) | 질문별 타이머 (15초) | QUIZ |
| [REVEAL](reveal.md) | 결과 공개 연출 (슬램/글리치/컨페티) | GRADE |
| [URL-ENCODE](url-encode.md) | 결과를 URL로 공유 | 없음 |
| [STYLE-DARK](style-dark.md) | 다크 테마 CSS | BASE |
| [STYLE-LIGHT](style-light.md) | 라이트 테마 CSS | BASE |
| [DEPLOY](deploy.md) | EC2 배포 파이프라인 | 없음 |

## 조합 예시

### "바이럴 O/X 테스트" (퐁퐁 같은)
```
BASE + DATA + SCREEN + QUIZ + TIMER + GRADE + REVEAL + SHARE + GA + STYLE-DARK
```

### "계산기" (월급계산기 같은)
```
BASE + DATA + SCREEN + CALC + GRADE + SHARE + GA + STYLE-LIGHT
```

### "다차원 분석" (MZ력, 엠생력 같은)
```
BASE + DATA + SCREEN + QUIZ + TIMER + GRADE + RADAR + REVEAL + URL-ENCODE + SHARE + GA + STYLE-LIGHT
```
