# hexalounge - 인증 기반 소셜 매칭 커뮤니티

> GitHub: https://github.com/ganna40/hexalounge

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 커뮤니티 플랫폼 (인증+게시판+매칭+채팅) |
| **한줄 설명** | 6가지 인증(연봉/외모/나이/직장/학벌/체형/MBTI)으로 신뢰도 쌓고, 게시판+매칭+1:1채팅하는 데이팅 커뮤니티 |
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
├── matching        일일 추천 3명 + 좋아요 → 매칭 성사
├── chat            1:1 채팅 (JSON 폴링 2초)
└── services/       공통 서비스 (badge, board_access, matching_service)
```

## 특수 기능

| 기능 | 설명 |
|------|------|
| **6각형 인증 시스템** | 연봉/외모/나이/직장/학벌/체형/MBTI — 서류 업로드 → Admin 심사 → 뱃지 자동 부여 |
| **뱃지 기반 접근 제어** | 게시판별 접근 조건 (public/tier/gender/verified) |
| **연봉 티어 (10단계)** | Iron~Challenger (LoL 스타일), 티어별 전용 게시판 |
| **일일 매칭 추천** | 매일 이성 3명 추천 (MBTI 궁합 + 지역 + 활동점수 + 랜덤) |
| **좋아요 → 매칭 → 채팅** | 양방향 좋아요 시 매칭 성사 + 72시간 채팅방 자동 생성 |
| **HTMX 인터랙션** | 좋아요/댓글/대댓글/무한스크롤/새로고침 — 페이지 리로드 없이 |
| **레이더 차트 (헥사그램)** | Canvas API로 6축 인증 진행도 시각화 |
| **Toss 디자인 시스템** | 토스 색상/라운딩/타이포/그림자 그대로 적용 |
| **CSS 애니메이션** | fadeUp 페이지 전환, floatY 이모지, emoji-glow 드롭섀도우 |
| **채팅 날짜 구분** | 날짜 변경 시 구분선 + 스크롤 시 sticky 날짜 헤더 |
| **토스트 알림** | fixed 오버레이 알림 (콘텐츠 밀림 방지) |
| **커스텀 뱃지 툴팁** | CSS ::after 툴팁 (data-tip 속성, JS 불필요) |
| **Django Admin 테마** | Toss 디자인으로 Admin 인터페이스 커스터마이징 |
| **Management Commands** | generate_recommendations (매일 18시), expire_matches (매일 0시) |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| **Django 6** | 풀스택 웹 프레임워크 (ORM, 템플릿, Admin, Signal, Middleware) |
| **HTMX 2.0** | 서버 렌더링 HTML을 부분 교체 (hx-get/post/target/swap) |
| **Tailwind CSS CDN** | 유틸리티 CSS (커스텀 색상 테마 `tailwind.config`) |
| **Alpine.js** | 간단한 프론트엔드 반응성 |
| **Canvas API** | 레이더 차트 (6축 헥사그램) |
| **Django ORM** | PostgreSQL/SQLite 모델 (User, Profile, Board, Post, Comment, Match, ChatRoom, Message) |
| **Django Signals** | User 생성 시 Profile/Verification 자동 생성 |
| **Django Custom Template Tags** | badge_html — raw badge → styled chip + tooltip |
| **JSON 폴링** | 채팅 새 메시지 2초 간격 fetch |

## DB 구조

```
accounts
├── Profile          성별, 닉네임, 출생연도, 지역, 뱃지(JSON), hex_score, 매칭설정

verification
├── Verification     salary/face/age/company/univ/body/mbti 각 verified 플래그 + status

community
├── Board            slug, board_type(public/tier/gender/verified), required_badge
├── Post             board FK, author, title, content, display_badges(JSON), like/comment/view count
├── Comment          post FK, parent FK(대댓글), display_badges(JSON)
├── PostLike         post + user unique_together
├── CommentLike      comment + user unique_together
├── PostReport       신고 (reason, detail)

matching
├── DailyRecommendation   user → target, date (unique_together)
├── Like                  sender → receiver (unique_together)
├── Match                 user_a ↔ user_b, expires_at(72h), is_active

chat
├── ChatRoom         match 1:1
├── Message          room FK, sender, content, is_read
```

## services 레이어

```
services/
├── badge_service.py       update_badges(), classify_univ(), tier_from_salary(), tier_to_int()
├── board_access.py        check_board_access(), can_access_board(), get_accessible_board_ids()
└── matching_service.py    get_daily_recommendations(), mbti_compatibility(), region_bonus()
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 hexalounge 레퍼런스를 보고
"{새 앱 이름}"을 만들어줘.
Django + HTMX + Tailwind CDN 조합.

- 인증 시스템: [필요한 인증 항목]
- 게시판: [접근 제어 조건]
- 매칭: [추천 알고리즘]
- 채팅: [JSON 폴링 / WebSocket]
- 디자인: Toss 디자인 시스템 (라이트 테마)
```
