# 더 가뿐 (The Gappun) - 건강기능식품 리뷰/쇼핑 플랫폼

> GitHub: https://github.com/ganna40/the_gappun

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 풀스택 쇼핑몰 (화해 클론) |
| **한줄 설명** | 건강기능식품 리뷰 랭킹 주문 MBTI 이벤트 플랫폼 |
| **타겟** | 건강기능식품 구매자 |
| **테마** | 라이트 (화해 스타일) |
| **폰트** | 시스템 폰트 (Apple SD Gothic Neo, Malgun Gothic) |

## 핵심 기능

| 기능 | 설명 |
|------|------|
| **JWT 인증** | access 30분 + refresh 7일, HTTPBearer scheme |
| **개인정보 수정** | 닉네임, 출생연도, 성별 수정 (PUT /users/me) |
| **체형 분석** | BMI 자동 계산 + 슬라이더 UI + 캐릭터 시각화 + 체형별 맞춤 추천 |
| **주문/결제** | 장바구니(프론트) - 결제 - 쿠폰 할인 적용 - 주문취소 시 쿠폰 복원 |
| **MBTI 이벤트** | 12문항 퀴즈 - MBTI 판정 - 자동 쿠폰 발급 + 상품별 차등 할인율 (3~20%) |
| **쿠폰 시스템** | Event - Coupon 템플릿 - UserCoupon 발급, 최소구매금액/최대할인 검증 |
| **랭킹** | 5종류 (급상승/카테고리/체형/연령대/브랜드) + 서브필터 pills |
| **배너 캐러셀** | 터치 스와이프 + 자동 슬라이드 + 7개 배너 |
| **브랜드 소개** | 브랜드 스토리 + 연혁 타임라인 + 보도자료 |
| **법적 페이지** | 이용약관 + 개인정보처리방침 + 사업자정보확인 |
| **드래그 스크롤** | useDragScroll 커스텀 훅 - 마우스 드래그로 가로 스크롤 |
| **호버 효과** | 카테고리, 어워드, 랭킹 카드에 shadow + scale 효과 |
| **트렌딩 일시정지** | 마우스 hover 시 자동 슬라이드 멈춤 (useRef) |

## 프론트엔드 페이지 (18개)

- / : 홈 (배너 캐러셀 + 카테고리 그리드 + 체형 맞춤 추천 + 어워드 + 트렌딩 + 랭킹 카드 + 인기상품 + 인기 브랜드)
- /rankings : 랭킹 (5종 탭: 급상승/카테고리/체형/연령대/브랜드 + 서브필터 pills + 드래그 스크롤)
- /awards : 어워드 목록 (이미지 카드 그리드 + 호버 효과)
- /awards/:id : 어워드 상세 (수상 제품 리스트)
- /brand : 브랜드 소개 (히어로 이미지 + 핵심 지표 + 미션 + 핵심 가치 + 연혁 타임라인 + 보도자료)
- /products/:id : 상품 상세 (성분, 리뷰, 별점 분포, 찜하기, 장바구니)
- /search : 검색
- /auth : 로그인/회원가입
- /mypage : 마이페이지 (개인정보 수정, 체형 분석 BMI 슬라이더, 쿠폰함, 주문내역, 찜 목록)
- /cart : 장바구니
- /checkout : 결제 (쿠폰 선택 + 할인 적용)
- /orders : 주문 내역
- /orders/:id : 주문 상세 + 취소
- /events/mbti : MBTI 퀴즈 이벤트
- /terms : 이용약관
- /privacy : 개인정보처리방침
- /business-info : 사업자정보확인

## UI/UX 패턴

| 패턴 | 적용 위치 | 구현 |
|------|-----------|------|
| **배너 캐러셀** | 홈 상단 | 터치 스와이프 + 4초 자동 슬라이드 + dot/page 인디케이터 |
| **드래그 스크롤** | 랭킹 필터 pills, 체형 추천, 브랜드 목록 | useDragScroll 커스텀 훅 (callback ref) |
| **호버 효과** | 카테고리, 어워드, 랭킹 카드 | group + hover:shadow-md + image scale-105/110 |
| **트렌딩 일시정지** | 홈 급상승 랭킹 | useRef로 pause state (리렌더 방지) + onMouseEnter/Leave |
| **BMI 시각화** | 마이페이지 | 슬라이더 - BMI 자동계산 - 색상 바 + 캐릭터 변경 |
| **이미지 워터마크 크롭** | 브랜드 페이지 히어로 | overflow-hidden + maxHeight:95vw + marginBottom:-5% |

## 삽질 방지

- seed.py drop_all 실패: FK 참조하는 모든 모델(Order, OrderItem, Event, MbtiProductDiscount, Coupon, UserCoupon)을 import 해야 함
- sed로 JS 문자열 편집 금지: sed가 백슬래시n을 실제 줄바꿈으로 삽입하여 파싱 에러 유발
- RankingType enum 불일치: body type 랭킹은 type=skin (body 아님) - 프론트/백엔드 일치 확인
- hover scale 안 보임: 부모에 overflow-hidden 없으면 확대된 이미지가 컨테이너 밖으로 넘침
- object-cover vs object-contain: 빈 공간 방지는 cover, 전체 이미지 보기는 contain
