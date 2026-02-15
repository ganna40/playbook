# hexalounge - 인증 기반 소셜 매칭 커뮤니티

> GitHub: https://github.com/ganna40/hexalounge

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 커뮤니티 플랫폼 (인증+게시판+매칭+채팅+포인트) |
| **한줄 설명** | 6가지 인증(연봉/외모/나이/직장/학벌/체형/MBTI)으로 신뢰도 쌓고, 3-Tier 매칭+게시판+1:1채팅하는 데이팅 커뮤니티 |
| **타겟** | 2030 직장인 (인증 기반 신뢰 커뮤니티) |
| **테마** | 라이트 (Toss 디자인 시스템) |
| **폰트** | 시스템 폰트 (-apple-system, Apple SD Gothic Neo, Pretendard, Noto Sans KR) |

## 모듈 조합

```
DJANGO + HTMX + Tailwind CDN + Alpine.js + Canvas RADAR + GRADE + DEPLOY
```

## 아키텍처

```
Django 6 (WSGI)
├── accounts        회원가입/로그인/프로필 (User + Profile 1:1)
├── verification    6가지 인증 (서류 업로드 → Admin 심사 → 뱃지)
├── community       게시판 CRUD (Board → Post → Comment, 접근 제어)
├── matching        3-Tier 매칭 추천 + 좋아요 → 매칭 성사
├── chat            1:1 채팅 (JSON 폴링 2초)
├── points          헥사 포인트 충전/소비 (월렛 시스템)
└── services/       공통 서비스 (badge, board_access, matching_service, wallet_service)
```

## 특수 기능

| 기능 | 설명 |
|------|------|
| **6각형 인증 시스템** | 연봉/외모/나이/직장/학벌/체형/MBTI — 서류 업로드 → Admin 심사 → 뱃지 자동 부여 |
| **인증 등급 세분화** | 외모(S/A/B), 자산(Lv.1~3), 직장(대기업/공기업/전문직 등) 등급별 뱃지 |
| **뱃지 기반 접근 제어** | 게시판별 접근 조건 (public/tier/gender/verified) |
| **연봉 티어 (10단계)** | Iron~Challenger (LoL 스타일), 티어별 전용 게시판 |
| **3-Tier 매칭 엔진** | Mirror(안정감, ±5점), Dream(상향, +5~20점), Destiny(운명, MBTI 궁합) |
| **인기도 점수 (Elo)** | Laplace smoothing `(좋아요+1)/(좋아요+패스+2)`, spec+popularity 합산 점수 |
| **UserInteraction 추적** | LIKE/PASS/MATCH 모든 상호작용 기록 + 인기도 실시간 갱신 |
| **중복 매칭 방지** | 이미 매칭된 유저 재매칭 차단 (like_view에서 기존 Match 확인) |
| **매칭 성사 애니메이션** | Canvas 파티클 버스트 (하트/별/원) + heartBeat + cardPop 바운스 |
| **좋아요 → 매칭 → 채팅** | 양방향 좋아요 시 매칭 성사 + 72시간 채팅방 자동 생성 |
| **보낸/받은 관심 목록** | 보낸 좋아요 상태 추적 (매칭됨/상호관심/대기중) |
| **매칭 목록 → 채팅** | 매칭된 상대 클릭 시 채팅방 직접 진입 + 슬라이드 전환 |
| **Admin 매칭 시뮬레이터** | 유저 선택 → 3-Tier 결과 시뮬레이션 + 대시보드 통계 8개 |
| **헥사 포인트 시스템** | 충전/소비 월렛 (관리자 충전, 서비스 내 소비) |
| **고스트 모드** | 일정 기간 매칭 추천에서 숨기기 |
| **HTMX 인터랙션** | 좋아요/댓글/대댓글/무한스크롤/새로고침 — 페이지 리로드 없이 |
| **레이더 차트 (헥사그램)** | Canvas API로 6축 인증 진행도 시각화 |
| **Toss 디자인 시스템** | 토스 색상/라운딩/타이포/그림자 그대로 적용 |
| **CSS 애니메이션** | fadeUp 페이지 전환, floatY 이모지, emoji-glow 드롭섀도우 |
| **채팅 날짜 구분** | 날짜 변경 시 구분선 + 스크롤 시 sticky 날짜 헤더 |
| **Django Admin 테마** | Toss 디자인으로 Admin 인터페이스 커스터마이징 |
| **Management Commands** | generate_recommendations, expire_matches, seed_test_users, backfill_interactions |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| **Django 6** | 풀스택 웹 프레임워크 (ORM, 템플릿, Admin, Signal, Middleware) |
| **HTMX 2.0** | 서버 렌더링 HTML을 부분 교체 (hx-get/post/target/swap) |
| **Tailwind CSS CDN** | 유틸리티 CSS (커스텀 색상 테마 `tailwind.config`) |
| **Alpine.js** | 간단한 프론트엔드 반응성 |
| **Canvas API** | 레이더 차트 (6축 헥사그램) + 매칭 성사 파티클 애니메이션 |
| **Django ORM** | SQLite 모델 (User, Profile, Board, Post, Comment, Match, ChatRoom, Message, UserInteraction, HexaWallet) |
| **Django Signals** | User 생성 시 Profile/Verification 자동 생성 |
| **Django Custom Template Tags** | badge_html — raw badge → styled chip + tooltip |
| **Django Admin Custom Views** | 매칭 시뮬레이터 (get_urls 오버라이드 + 커스텀 template) |
| **JSON 폴링** | 채팅 새 메시지 2초 간격 fetch |

## DB 구조

```
accounts
├── Profile          성별, 닉네임, 출생연도, 지역, 뱃지(JSON), hex_score, popularity_score, 매칭설정, ghost_mode

verification
├── Verification     salary/face/age/company/univ/body/mbti 각 verified 플래그 + status
│                    appearance_tier(S/A/B), asset_img, company_doc, company_type

community
├── Board            slug, board_type(public/tier/gender/verified), required_badge
├── Post             board FK, author, title, content, image, display_badges(JSON), like/comment/view count
├── Comment          post FK, parent FK(대댓글), display_badges(JSON)
├── PostLike / CommentLike / PostReport

matching
├── DailyRecommendation   user → target, date (unique_together)
├── Like                  sender → receiver (unique_together)
├── Match                 user_a ↔ user_b, expires_at(72h), is_active
├── UserInteraction       from_user → to_user, action(LIKE/PASS/MATCH), unique_together

chat
├── ChatRoom         match 1:1
├── Message          room FK, sender, content, is_read

points
├── HexaWallet       user 1:1, balance
├── HexaTransaction  wallet FK, type(charge/spend), amount, description
```

## services 레이어

```
services/
├── badge_service.py       update_badges(), classify_univ(), tier_from_salary(), tier_to_int()
├── board_access.py        check_board_access(), can_access_board(), get_accessible_board_ids()
├── matching_service.py    get_daily_matches() [3-Tier], total_score(), calculate_popularity_score(),
│                          update_popularity_score(), _get_base_candidates(), spec_score(),
│                          mbti_compatibility(), region_bonus(), get_daily_recommendations() [호환]
└── wallet_service.py      charge(), spend(), get_balance()
```

## 3-Tier 매칭 알고리즘

```
전제 필터:
  이성 + hex_score≥1 + 활성(7일 내 접속) + 고스트 모드 아님
  + 이전 상호작용 없음 + 이미 매칭 안 됨 + 나이/지역 소프트 필터

Tier 1 - Mirror (안정감):
  내 total_score ±5 범위 → 점수 차이 작은 상위 5명 중 랜덤 1명

Tier 2 - Dream (상향):
  내 total_score +5~20 범위 → 범위 내 최고 점수 1명

Tier 3 - Destiny (운명):
  점수 무관 → MBTI 궁합 최고 상위 3명 중 랜덤 1명

Fallback: 후보 부족 시 → 최근 접속순 정렬로 채움

total_score = spec_score(0~100) + popularity_score * 10(0~10) = 0~110
popularity_score = (좋아요+1) / (좋아요+패스+2)  (Laplace smoothing)
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 hexalounge 레퍼런스를 보고
"{새 앱 이름}"을 만들어줘.
Django + HTMX + Tailwind CDN 조합.

- 인증 시스템: [필요한 인증 항목]
- 게시판: [접근 제어 조건]
- 매칭: [3-Tier 알고리즘 / 단순 추천]
- 채팅: [JSON 폴링 / WebSocket]
- 포인트: [충전/소비 시스템 필요 여부]
- 디자인: Toss 디자인 시스템 (라이트 테마)
```
