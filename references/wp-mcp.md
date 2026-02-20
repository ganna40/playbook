# wp-generation-mcp - WordPress SEO MCP 서버

> GitHub: https://github.com/ganna40/wp-generation-mcp
> 로컬: C:\Users\ganna\Downloads\wp-generation-mcp

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | MCP 서버 (개발 자동화 도구) |
| **한줄 설명** | Claude Code에서 WordPress 글 작성→SEO→스타일 체크→예약 발행 자동화 |
| **타겟** | WordPress SEO 블로거, AI 자동화 개발자 |
| **스택** | Python + FastMCP + httpx + WordPress REST API + RankMath API |

## 모듈 조합

```
FastMCP + WordPress REST API + RankMath REST API + Pexels API + Code Snippets REST API
```

## 17개 MCP 도구

| 도구 | 용도 |
|------|------|
| `wp_check_connection` | 연결 + 인증 + RankMath 확인 |
| `wp_keyword_research` | Google 자동완성 키워드 리서치 |
| `wp_check_cannibalization` | 기존 글 키워드 중복 체크 |
| `wp_create_post` | 글 생성 (SEO 메타 자동 설정, 슬러그 자동 생성) |
| `wp_update_post` | 글 수정 |
| `wp_list_posts` | 글 목록 |
| `wp_get_post` | 글 상세 조회 |
| `wp_list_drafts` | 초안/예약 글 목록 |
| `wp_seo_check` | **SEO 분석 + 구체적 수정 제안** (실패 항목별 액션 포함) |
| `wp_find_image` | Pexels/Unsplash/Pixabay 이미지 검색 + WP 업로드 |
| `wp_upload_media` | URL → WP 미디어 업로드 |
| `wp_find_internal_links` | **3단계 유사도 매칭 내부 링크 추천** |
| `wp_review_draft` | 초안 종합 리뷰 (서버사이드 SEO 점수) |
| `wp_schedule_draft` | 예약 발행 (ISO 8601 날짜) |
| `wp_publish_pipeline` | 이미지→글생성→리뷰 통합 파이프라인 |
| `wp_seo_optimize` | 기존 글 SEO 자동 최적화 (슬러그, 이미지, 문단 분리, H2 구조) |
| `wp_style_check` | **AI 문체 패턴 감지** (문단 다양성, 1인칭, 구어체, 여담) |

## 핵심 강화 도구 상세

### wp_seo_check — SEO 분석 + 수정 제안

기존 20개 체크리스트 출력 후, 실패 항목에 대해 **구체적 수정 방법**을 생성:

| 실패 항목 | 제안 내용 |
|---|---|
| 첫 문단 키워드 | 첫 문단 원문 발췌 + 키워드 삽입 예시 |
| 키워드 밀도 과다 | 제거 대상 문장 나열 + 동의어 제안 |
| 키워드 밀도 부족 | 삽입 가능한 위치(키워드 없는 문단) 나열 |
| 소제목 키워드 | 키워드 없는 H2 목록 + 삽입 예시 |
| 내부 링크 | WP 검색으로 관련 글 3개 HTML 링크 제공 |
| 외부 링크 | 추가 안내 |
| 메타/제목 | 현재 길이 + 목표 범위 + 수정 방향 |

### wp_find_internal_links — 3단계 유사도 매칭

```
1단계: 포커스 키워드 매칭 (Jaccard 유사도)
  - /custom/v1/posts-keywords 엔드포인트로 기존 글의 focus_keyword 비교
  - 정확 매칭 10점, 부분 매칭 sim * 7점

2단계: WP 검색 API (제목 + excerpt)
  - 제목 단어 매칭 최대 5점, excerpt 최대 3점

3단계: 카테고리 보너스
  - 같은 카테고리 +3점

결과: 점수별 등급 (🔴 8+ / 🟡 4+ / ⚪) + 양방향 링크 제안
```

### wp_style_check — AI 문체 패턴 감지

| 체크 항목 | 기준 |
|---|---|
| 문단 길이 분포 | 변동계수 0.4+ 필요, 짧은 문단 있어야 함 |
| 1인칭 표현 | "저는", "직접", "해봤", "경험상" 등 3회 이상 |
| 구어체 전환어 | "솔직히", "근데", "여담인데" 등 2회 이상 |
| 섹션 도입 다양성 | 연속 3개 H2 뒤 같은 단어로 시작하면 경고 |
| 문장 시작 다양성 | 첫 글자 고유 비율 50%+ |
| 여담/비유 | "여담", "비유하자면", "마치~처럼" 등 1회 이상 |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| **FastMCP** | Python MCP 서버 프레임워크 |
| **WordPress REST API** | 글/카테고리/태그/미디어 CRUD (`/wp-json/wp/v2/`) |
| **RankMath REST API** | SEO 메타 쓰기 (`/wp-json/rankmath/v1/updateMeta`) |
| **Code Snippets REST API** | PHP 스니펫 (SEO 점수 + posts-keywords endpoint) |
| **Pexels API** | 무료 스톡 이미지 검색 (가로 방향, 포커스 키워드 alt) |
| **Google 자동완성 API** | 키워드 리서치 (API 키 불필요) |
| **httpx** | 비동기 HTTP 클라이언트 |
| **python-dotenv** | 환경변수 관리 (.env) |

## 아키텍처

```
Claude Code
  ↓ (MCP 프로토콜)
wordpress_mcp.py (FastMCP 서버, 17개 도구)
  ↓ (HTTP)
WordPress REST API (/wp-json/wp/v2/)
RankMath REST API (/wp-json/rankmath/v1/)
Custom REST API:
  /wp-json/custom/v1/seo-score/{id}    ← SEO 점수 계산
  /wp-json/custom/v1/posts-keywords     ← 내부 링크 매칭용
Pexels API (이미지 검색)
Google Autocomplete (키워드 리서치)
```

## 파이프라인

```
키워드 리서치 → 카니발리제이션 체크
  → 이미지 검색 + WP 업로드 + 본문 자동 삽입
  → 글 생성 (draft) + RankMath SEO 메타 설정
  → SEO 체크 (수정 제안 포함)
  → 스타일 체크 (AI 패턴 감지)
  → 서버사이드 SEO 점수 계산 (PHP endpoint)
  → 종합 리뷰 리포트
  → 사용자 확인 후 예약 발행
```

## WordPress 필수 구성

- **RankMath SEO** 플러그인
- **Code Snippets** 플러그인 (서버사이드 SEO endpoint용)
  - 스니펫 1: RankMath REST API Meta Fields (`rank_math_seo_score` 등 `show_in_rest` 등록)
  - 스니펫 2: Server-side SEO Score Calculator (`/custom/v1/seo-score/{id}`)
  - 스니펫 3: Posts-Keywords endpoint (`/custom/v1/posts-keywords`, 1시간 캐시)
- **애플리케이션 비밀번호** (사용자 → 프로필 → 애플리케이션 비밀번호)

## 삽질 포인트

| 문제 | 해결 |
|------|------|
| RankMath 점수가 REST API에서 안 읽힘 | Code Snippets로 `register_post_meta()` + `show_in_rest => true` 추가 |
| RankMath 점수가 에디터에서만 계산됨 | PHP 커스텀 REST endpoint로 서버사이드 점수 계산 구현 |
| WP REST API `meta` 필드로 RankMath 메타 저장 안됨 | RankMath 자체 API `/rankmath/v1/updateMeta` 사용 |
| 포커스 키워드가 URL에 안 들어감 | `_keyword_to_slug()` 헬퍼로 자동 생성 |
| Windows cp949 인코딩 에러 | `PYTHONIOENCODING=utf-8` 환경변수 |
| 내부 링크 추천 품질 낮음 | 3단계 매칭 알고리즘 (포커스키워드 유사도 + 검색 + 카테고리) |

## AI에게 비슷한 거 만들게 하려면

```
playbook의 wp-mcp 레퍼런스를 보고
WordPress MCP 서버를 다른 CMS(Ghost, Notion 등)에 맞게 포팅해줘.
FastMCP + httpx + REST API 조합.
```
