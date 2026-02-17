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
- **Anthropic Claude SDK** — 프로젝트 카테고리/예산/일정 자동 분석, 코드 리뷰 견적

### 파일
- **AWS S3** — Presigned URL 기반 파일 업로드 (이미지, 문서)

---

## 주요 기능

### 카테고리 (7개)
웹 개발, 앱 개발, 데이터/AI, 디자인, 기획/PM, 기타, 코드 리뷰/유지보수

### AI 견적 분석
- `POST /api/ai/analyze` — Claude가 프로젝트 설명을 분석
- 카테고리 자동 추천, 예산 범위, 예상 일정, 필요 스킬 도출
- 카테고리별 기본값(minPrice/maxPrice/minDays/maxDays) 폴백

### 개발자 등급 시스템
```
ROOKIE (신입)  → SILVER (실버)  → GOLD (골드)  → MASTER (마스터)
avgRating 기반, completedCount 가중
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
- `/` — 랜딩 (카테고리 목록 + AI 견적 CTA)
- `/projects` — 프로젝트 목록 (카테고리/상태 필터)
- `/projects/[id]` — 프로젝트 상세 + 제안하기
- `/developers` — 개발자 목록 (스킬/등급 필터)
- `/developers/[id]` — 개발자 공개 프로필
- `/code-review` — 코드 리뷰 서비스 소개 + AI 견적
- `/guide`, `/faq`, `/contact`

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
