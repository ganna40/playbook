# hexaconsulting - 연애 컨설팅 퍼널

> GitHub: https://github.com/ganna40/hexaconsulting

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 세일즈 퍼널 (바이럴 진단 → 결과 → 랜딩 → 결제) |
| **한줄 설명** | 20문항 연애 진단 → 찌그러진 육각형 결과 → 전문가 컨설팅 랜딩 → PortOne 결제 |
| **타겟** | 2030 연애 고민자 (비회원 퍼널, 로그인 없음) |
| **테마** | 라이트 (Toss 디자인 시스템) |
| **폰트** | 시스템 폰트 (-apple-system, Apple SD Gothic Neo, Pretendard, Noto Sans KR) |

## 모듈 조합

```
DJANGO + HTMX + Tailwind CDN + Alpine.js + Canvas RADAR + Pillow OG + PortOne + DEPLOY
```

## 아키텍처

```
Django 6 (WSGI)
├── diagnosis       20문항 테스트 + 6축 결과 + OG 이미지 생성
├── consulting      세일즈 랜딩 + 결제 (PortOne) + 주문 관리
└── templates/      base.html (Toss 디자인) + 앱별 템플릿
```

## 특수 기능

| 기능 | 설명 |
|------|------|
| **HTMX 1문항씩 전환** | hx-post로 한 문항씩 교체, 프로그레스 바 포함 파셜 스왑 |
| **6축 육각형 차트** | Canvas API 레이더 차트 — 찌그러진 모양으로 약점 시각화 |
| **수능 등급 시스템 (1~9)** | 축별 점수(0~100)를 수능 분위표 기준 1~9등급으로 매핑 |
| **불균형 감지** | max-min gap ≥ 40이면 "불균형 (스펙형 인간)" 등 특수 라벨 부여 |
| **등급 체계 (S~D)** | S/A/B+/B/B-/C/D — 평균 + 불균형 gap 기반 판정 |
| **IP 기반 중복제거 카운팅** | DiagnosisSession.unique_count() — IP별 distinct count |
| **Pillow OG 이미지 동적 생성** | 800x800 정사각형 PNG — 등급 + 육각형 차트 + 축별 점수 |
| **SNS 공유 (4채널)** | 카카오톡(JS SDK) / 텔레그램 / X / 인스타그램(캡처 유도) |
| **html2canvas 캡처** | 결과 영역 캡처 → PNG 다운로드 (워터마크 포함) |
| **결과 URL 공유** | /result/<session_key>/ — 비회원도 결과 공유 가능 |
| **PortOne 결제** | iamport.js SDK + 서버 검증 (verify_payment) |
| **FOMO 타이머** | 랜딩 페이지 카운트다운 + 할인율 표시 |
| **FAQ 아코디언** | Alpine.js x-show 토글 |
| **Toss Admin 테마** | Django Admin에 Toss 디자인 CSS 오버라이드 |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| **Django 6** | 풀스택 (세션 기반 비회원 흐름, ORM, Admin) |
| **HTMX 2.0** | 문항 전환 (hx-post → 파셜 스왑), HX-Redirect로 결과 이동 |
| **Tailwind CSS CDN** | 커스텀 테마 (hexa/accent/surface/content 색상) |
| **Alpine.js** | FAQ 아코디언, 타이머, 인터랙션 |
| **Canvas API** | 6축 레이더 차트 (점 색상: 파랑/노랑/빨강 등급별) |
| **Pillow (PIL)** | OG 이미지 서버사이드 렌더링 (한글 NotoSansCJK 폰트) |
| **html2canvas** | 클라이언트 결과 캡처 → PNG 다운로드 |
| **Kakao JS SDK** | Kakao.Share.sendDefault() 피드 공유 |
| **PortOne (iamport)** | html5_inicis PG 결제 + REST API 검증 |

## DB 구조

```
diagnosis
├── QuestionCategory     6축 (외모/능력/소통/센스/경험/관리), slug, axis_label, order
├── Question             category FK, text, part(A:하드웨어/B:소프트웨어), order
├── Choice               question FK, text, score(0~10), order
├── DiagnosisSession     session_key(unique), scores(JSON), grade, grade_label, ip_address

consulting
├── ConsultingProduct    name, slug, price, original_price, emoji, features(JSON)
├── ConsultingOrder      order_id(UUID), product FK, diagnosis FK, user_phone, amount, status, payment_id
├── Testimonial          title, content, before_text, after_text
```

## 퍼널 흐름

```
인트로 (/)
  ├── 참여자 수 카운터 (IP 기반 unique count)
  └── CTA: "무료 진단 시작하기"
      ↓
테스트 (/test/)
  ├── Part A (하드웨어) 5문항 → Part B (소프트웨어) 15문항
  ├── HTMX 파셜 스왑 (프로그레스 바 + 문항)
  └── 마지막 문항 → HX-Redirect → /result/
      ↓
결과 (/result/)
  ├── 등급 (S~D) + 수능 등급 (1~9)
  ├── 찌그러진 육각형 차트
  ├── 축별 점수 바 + 수능 등급 뱃지
  ├── SNS 공유 (카카오/텔레그램/X/인스타) + 캡처 저장
  └── CTA: "내 육각형 채우는 방법 보기"
      ↓
랜딩 (/consulting/)
  ├── 문제 제기 → 권위 부여 → 해결책 → 상품 3개 → FOMO → FAQ
  └── 상품 선택 → /consulting/checkout/<slug>/
      ↓
결제 (/consulting/checkout/)
  ├── 전화번호/이름 입력 → PortOne SDK 결제
  └── 서버 검증 → /consulting/complete/
```

## 수능 등급 매핑

```python
SUNEUNG_GRADES = [
    (96, 1), (89, 2), (77, 3), (60, 4), (40, 5),
    (23, 6), (11, 7), (4, 8), (0, 9),
]
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 hexaconsulting 레퍼런스를 보고
"{새 앱 이름}" 진단 퍼널을 만들어줘.
Django + HTMX + Tailwind CDN 조합.

- 진단: [문항 수, 카테고리 축 수]
- 결과: [육각형 차트 / 바 차트 / 점수표]
- 등급: [S~D / 수능 1~9 / 커스텀]
- 공유: [카카오톡 / 텔레그램 / X / 인스타]
- OG 이미지: [Pillow 동적 생성 / 정적]
- 결제: [PortOne / 토스페이먼츠 / 없음]
- 디자인: Toss 디자인 시스템 (라이트 테마)
```
