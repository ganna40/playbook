# food - 오늘 뭐먹지?

> URL: (로컬 개발 중)
> GitHub: https://github.com/ganna40/food

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 추천기 (질문 → GPS 맛집 랜덤 추천) |
| **한줄 설명** | 3가지 질문 + GPS 위치 → 주변 맛집 랜덤 추천 + 별점 필터 |
| **타겟** | 점심/저녁 메뉴 고민하는 사람 |
| **테마** | 라이트 (파스텔 그라데이션) |
| **폰트** | Noto Sans KR (Google Fonts) |

## 기술 스택

> **기존 앱들과 다른 스택.** 바닐라 HTML SPA가 아니라 Svelte + Vite 빌드 시스템.

| 기술 | 용도 |
|------|------|
| **Svelte 5** | UI 프레임워크 (컴포넌트 기반) |
| **TypeScript** | 타입 안전성 |
| **Vite 7** | 빌드 + 개발 서버 + API 프록시 |
| **Tailwind CSS v3** | 빌드 방식 (tailwind.config.js) |
| **Kakao Local REST API** | 키워드 장소 검색 (반경 2km) |
| **카카오맵 Place API** | 별점 크롤링 (place.map.kakao.com) |
| **Geolocation API** | GPS 위치 기반 |
| **Noto Sans KR** | Google Fonts 웹폰트 |

## 화면 흐름

```
start (시작하기)
  → location (GPS 위치 확인 / 주소 입력)
    → question × 3 (기분, 음식종류, 시간여유)
      → rating-filter (별점 필터: 상관없음/3.5+/4.0+/4.5+)
        → loading (맛집 검색 + 별점 분석 진행바)
          → result (맛집 추천 + confetti)
            → 다시 뽑기 (거부 목록에 추가)
            → 이거로 할게요! → complete (지도보기/다른메뉴)
```

## 질문 → 키워드 매핑

3개 질문의 답변 조합으로 검색 키워드를 결정:

```typescript
// 예: 기분 좋아 + 고기 + 여유있어 → ['삼겹살', '스테이크', '갈비']
// 예: 피곤 + 국물 + 바빠 → ['국밥', '설렁탕', '칼국수']
keywordMap[mood][food][time] → string[]  // 3개 키워드
```

| 기분 | 음식 | 시간 | 키워드 예시 |
|------|------|------|------------|
| 좋아 | 고기 | 여유 | 삼겹살, 스테이크, 갈비 |
| 지침 | 국물 | 바빠 | 국밥, 설렁탕, 칼국수 |
| 그냥 | 아무거나 | 여유 | 중식, 일식, 양식 |

## 핵심 기능

| 기능 | 설명 |
|------|------|
| **GPS 위치 검색** | Geolocation API로 현재 위치, 실패 시 주소 입력 |
| **Kakao Local API** | 키워드 + 좌표 + 반경 2km 식당 검색 (FD6 카테고리) |
| **별점 크롤링** | 카카오맵 place 페이지에서 별점 파싱 (JSON + regex) |
| **별점 필터** | 상관없음 / 3.5+ / 4.0+ / 4.5+ 선택 |
| **다시 뽑기** | 거부한 식당 Set에 추가, 나머지에서 재추천 |
| **Vite Proxy** | `/api/kakao` → `dapi.kakao.com` 프록시로 API 키 숨김 |
| **진행바** | 별점 분석 시 `current/total` 프로그레스바 |
| **Confetti 연출** | 결과 화면에서 CSS confetti-fall 애니메이션 |

## API 키 관리

Kakao REST API 키를 Vite 환경변수로 관리:

```bash
# .env (로컬)
VITE_KAKAO_API_KEY=your_rest_api_key
```

Vite proxy에서 `KakaoAK ${env.VITE_KAKAO_API_KEY}` 헤더를 자동 주입.
→ 브라우저에 API 키가 노출되지 않음.

## 프로젝트 구조

```
food/
├── index.html              # Noto Sans KR 폰트 로드
├── vite.config.ts          # Vite + Svelte + Kakao API 프록시
├── tailwind.config.js      # Tailwind v3 설정
├── src/
│   ├── main.ts             # Svelte 마운트
│   ├── app.css             # Tailwind directives + 폰트 설정
│   ├── App.svelte          # 메인 (화면 전환, 상태 관리)
│   └── lib/
│       ├── components/
│       │   ├── Question.svelte   # 질문 카드 (이모지 버튼)
│       │   └── Result.svelte     # 결과 카드 (confetti)
│       ├── data/
│       │   └── questions.ts      # 질문 + 키워드 매핑
│       └── api/
│           └── kakao.ts          # 카카오 API 호출 + 별점 크롤링
```

## 기존 앱과의 차이

| 항목 | 기존 앱 (salary, pong 등) | food |
|------|---------------------------|------|
| 프레임워크 | 바닐라 HTML/JS | Svelte 5 + TypeScript |
| 빌드 | 없음 (CDN) | Vite 7 |
| CSS | Tailwind CDN / 순수 CSS | Tailwind v3 빌드 |
| API | Kakao JS SDK (공유) | Kakao Local REST API (검색) |
| 데이터 | JSON 파일 / 인라인 | TypeScript 인라인 |
| 공유 | 카카오톡 + URL + 스크린샷 | 없음 |
| GA | 있음 | 없음 |

## AI에게 비슷한 거 만들게 하려면

```
playbook의 food 레퍼런스를 보고
"주변 카페 추천기"를 만들어줘.
Svelte + Vite + Tailwind + Kakao Local API.
- 3가지 질문 (분위기, 음료종류, 인원)
- GPS 기반 반경 1km 카페 검색
- 별점 필터 포함
- food와 동일한 구조
```
