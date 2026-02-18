# vibejob - 바이브잡 (프리랜서 매칭 플랫폼)

> 바이브코더 전문 외주 매칭 플랫폼. AI 견적 + 에스크로 결제 + 등급 시스템.

---

## 개요

| 항목 | 값 |
|------|-----|
| 유형 | 프리랜서 매칭 플랫폼 |
| 스택 | Next.js 15 + React 19 + Prisma 6 + NextAuth 5 + Tailwind v4 + shadcn/ui |
| 테마 | 라이트 (커스텀 디자인 시스템) |
| 상태 | 개발 중 |

---

## 핵심 플로우

```
의뢰자: 프로젝트 등록 → AI(Claude) 카테고리/예산/일정 자동 분석
      → 개발자 제안 수신 → 매칭 수락
      → 에스크로 결제 → 마일스톤 관리 → 검수 → 리뷰

개발자: 프로필 설정 (스킬/포트폴리오)
      → 프로젝트 탐색 → 제안서 작성
      → 매칭 → 작업 → 마일스톤 완료 → 정산(월렛)

관리자: 유저/프로젝트/결제 대시보드 (전체 통계)
```

---

## 기술 스택

### 프론트엔드
- **React 19** — 최신 React
- **Tailwind CSS v4** — `@theme` 블록으로 커스텀 색상, PostCSS 빌드
- **shadcn/ui** — Radix UI + class-variance-authority + tailwind-merge
- **Lucide-React** — 아이콘
- TypeScript 5.7

### 백엔드
- **Next.js 15 App Router** — API Routes + 서버/클라이언트 컴포넌트
- **NextAuth.js 5** (Auth.js) — Credentials Provider + Prisma Adapter
- **Prisma ORM 6** — 스키마 → 마이그레이션 → 타입세이프 클라이언트
- **bcryptjs** — 비밀번호 해싱

### 데이터
- **PostgreSQL** — Prisma 통해 접근
- **Zod** — API 입력 스키마 검증

### AI
- **Ollama (로컬 LLM)** — 프로젝트 카테고리/예산/일정 자동 분석, 코드 리뷰 견적
- (Anthropic SDK 제거 → Ollama 전환)

### 파일
- **AWS S3** — Presigned URL 기반 파일 업로드 (이미지, 문서)

### 보안
- **Redis Rate Limiting** — AI 엔드포인트 IP당 5회/분 제한
- **crypto.randomUUID()** — 결제 merchantUid 보안 강화

---

## 주요 기능

### 카테고리 (7개)
웹 개발, 앱 개발, 데이터/AI, 디자인, 기획/PM, 기타, 코드 리뷰/유지보수

### AI 견적 분석
- `POST /api/ai/analyze` — Claude가 프로젝트 설명을 분석
- 카테고리 자동 추천, 예산 범위, 예상 일정, 필요 스킬 도출
- 카테고리별 기본값(minPrice/maxPrice/minDays/maxDays) 폴백

### 개발자 등급 시스템 (7티어)
```
ROOKIE(루키,40%) → SILVER(실버,35%) → GOLD(골드,30%) → PLATINUM(플래티넘,25%)
→ DIAMOND(다이아몬드,20%) → MASTER(마스터,15%) → GRANDMASTER(그랜드마스터,10%)

승급 조건: avgRating + completedCount + 뱃지 가중
수수료: 등급 올라갈수록 플랫폼 수수료 감소 (40% → 10%)
신규 개발자 매칭 부스트: completedCount < 3이면 기본 10점 부여
```

### 에스크로 결제
```
PENDING → HELD (에스크로 보관) → RELEASED (정산) or REFUNDED (환불)
```

### 마일스톤
프로젝트를 단계별로 분리, 각 마일스톤 완료 시 부분 정산 가능

### 1:1 채팅
프로젝트별 채팅방, 클라이언트-개발자 직접 소통

### 알림 시스템
헤더 벨 아이콘 배지 + 알림 목록 페이지

---

## 페이지 구조

### 공개 페이지
- `/` — 홈 (카테고리 목록 + AI 견적 CTA)
- `/about` — 회사소개 랜딩 (히어로 RotatingText + 스크롤 리빌 + 등급바 + 마키)
- `/projects` — 프로젝트 목록 (카테고리/상태 필터)
- `/projects/[id]` — 프로젝트 상세 + 제안하기
- `/developers` — 개발자 목록 (스킬/등급 필터)
- `/developers/[id]` — 개발자 공개 프로필
- `/code-review` — 코드 리뷰 서비스 소개 + AI 견적
- `/guide`, `/faq`, `/contact`, `/privacy`, `/terms`

### 의뢰자 (Client)
- `/client/dashboard` — 프로젝트 현황 + 최근 알림
- `/client/projects` — 내 프로젝트 관리
- `/client/payments` — 결제 내역 (에스크로/정산/환불 합계)

### 개발자 (Developer)
- `/developer/dashboard` — 등급/평점/월렛/활성 프로젝트
- `/developer/projects` — 진행 중 프로젝트 + 마일스톤
- `/developer/proposals` — 제안 목록 + 철회
- `/developer/portfolio` — 완료 프로젝트 + 리뷰
- `/developer/profile` — 프로필 편집
- `/developer/wallet` — 정산 내역

### 관리자 (Admin)
- `/admin` — 대시보드 (유저/프로젝트/매출/분쟁 통계)
- `/admin/users` — 유저 관리 (역할 필터 + 검색)
- `/admin/projects` — 프로젝트 관리 (상태 필터 + 검색)
- `/admin/payments` — 결제 관리 (상태 필터 + 합계)
- `/admin/applications` — 개발자 지원 심사
- `/admin/disputes` — 분쟁 관리 (환불/정산)
- `/admin/reviews` — 리뷰 관리
- `/admin/content` — 카테고리 관리
- `/admin/settings` — 플랫폼 설정 (수수료율, 시스템 통계)

---

## 아키텍처 패턴

### 클라이언트 사이드 페치 패턴 (속도 최적화)
```typescript
// 모든 대시보드 페이지: 서버 컴포넌트 → 클라이언트 사이드 fetch로 전환
// 결과: force-dynamic 1~2초 대기 → 즉시 네비게이션 + 로딩 스피너
"use client";
const [data, setData] = useState<T | null>(null);
const fetchData = useCallback(() => {
  setData(null);
  fetch(`/api/...?${qs}`).then(r => r.json()).then(setData);
}, [deps]);
useEffect(() => { fetchData(); }, [fetchData]);
```

### URL 기반 필터/페이지네이션
```typescript
const searchParams = useSearchParams();
const page = parseInt(searchParams.get("page") || "1");
const status = searchParams.get("status") || "";
// buildUrl({ status: "OPEN", page: "1" }) → Link href로 사용
```

### API 라우트 패턴
```typescript
// src/app/api/[role]/[resource]/route.ts
export async function GET(request: NextRequest) {
  const session = await auth();
  if (!session?.user) return NextResponse.json({error: "..."}, {status: 401});
  // Prisma 쿼리 → JSON 응답
}
```

---

## 디자인 시스템

### 커스텀 컬러 (@theme)
```css
@theme {
  --color-primary: #3182f6;
  --color-bg: #ffffff;
  --color-bg-secondary: #f8f9fa;
  --color-bg-tertiary: #f1f3f5;
  --color-text: #191f28;
  --color-text-secondary: #4e5968;
  --color-text-tertiary: #8b95a1;
  --color-border: #e5e8eb;
  --color-success: #22c55e;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
}
```

### shadcn/ui 컴포넌트
Card, Badge, Button, Avatar, Dialog, DropdownMenu, Select, Tabs, Toast, Progress, Tooltip, ScrollArea

---

## 랜딩페이지 (/about) 인터랙션

### 히어로
- **RotatingText**: 단어 타이핑(70ms/char) → 2.2초 정지 → 삭제(35ms/char) → 다음 단어 루프
  - "현실이 됩니다." → "서비스가 됩니다." → "사업이 시작됩니다."
- **Staggered entrance**: CSS `hero-line` 클래스 + `animation-delay` (0~700ms)
- **마우스 패럴랙스**: 그라데이션 orb가 마우스 따라 이동 (`mousemove` 이벤트)
- **블링킹 커서**: `.animate-cursor-blink` (0.8초 주기)
- **그라데이션 언더라인**: 타이핑 진행률에 따라 width 애니메이션

### 스크롤 리빌 (4종)
- `.scroll-reveal` — 아래→위 fadeUp
- `.scroll-reveal-left` — 왼쪽→오른쪽 슬라이드
- `.scroll-reveal-right` — 오른쪽→왼쪽 슬라이드
- `.scroll-reveal-scale` — 축소→확대
- `data-delay="100~400"` — 자식 시차 애니메이션
- 단일 IntersectionObserver로 모든 요소 감시 → `.is-visible` 클래스 토글

### 인터랙티브 컴포넌트
- **Counter**: 숫자 카운트업 애니메이션 (IntersectionObserver 트리거)
- **GradeBar**: 7개 등급 프로그레스 바 (호버 시 색상 변경)
- **AnimatedEstimate**: AI 견적 목업 3단계 애니메이션
- **AnimatedMilestones**: 에스크로 마일스톤 체크 애니메이션
- **Marquee**: AI 도구 무한 스크롤 (30초 주기, 호버 시 정지)

---

## UX 인프라

### Toast 시스템
- Radix UI `@radix-ui/react-toast` 기반
- `useToast()` hook → `toast({ title, description, variant })`
- 성공/에러/경고 3종 variant

### Error Boundary
- 4개: `/error.tsx` (root), `/admin/error.tsx`, `/client/error.tsx`, `/developer/error.tsx`
- "오류가 발생했습니다" + 재시도 버튼

### 분쟁 처리 시스템
- 클라이언트: `POST /api/projects/[id]/dispute` → DISPUTED 전환
- 관리자: `POST /api/admin/disputes` → 환불(refund) 또는 정산(release)

---

## AI에게 비슷한 거 만들게 하려면

```
playbook의 vibejob 레퍼런스를 보고
"새 매칭 플랫폼"을 만들어줘.
Next.js 15 + React 19 + Prisma + NextAuth + Tailwind v4 조합.
7티어 등급 시스템, 에스크로 결제, AI 견적, 스크롤 리빌 랜딩페이지.
```
