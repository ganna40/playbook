# life-sim-rpg - 인생 시뮬레이션 RPG

> 로컬: C:\Users\ganna\life-sim-rpg

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 인생 시뮬레이션 게임 (브라우저 RPG) |
| **한줄 설명** | 출생부터 사망까지 인생을 시뮬레이션하는 아이소메트릭 2D RPG |
| **스택** | React 19 + TypeScript + Vite 7 + Tailwind CSS v4 + Zustand 5 |
| **테마** | 다크 (Lineage 스타일 금/검정) |
| **폰트** | 시스템 폰트 |

## 기술 스택

```
React 19 + TypeScript + Vite 7 + Tailwind CSS v4 + Zustand 5
Canvas 2D (아이소메트릭 렌더러) + 커스텀 게임 엔진
```

## 아키텍처

```
src/
├── engine/           # 게임 엔진 (순수 TypeScript, UI 의존 없음)
│   ├── GameEngine.ts        # 메인 엔진 (dayTick, 시스템 통합)
│   ├── GameLoop.ts          # requestAnimationFrame 루프
│   ├── TimeSystem.ts        # 시간 관리 (년/월/일, 속도 조절)
│   ├── StatLevelSystem.ts   # 능력치 레벨링 (Lv.1-999, 성장/감쇠)
│   ├── AchievementSystem.ts # 업적 시스템 (33개 마일스톤)
│   ├── CareerSystem.ts      # 직업/승진/월급 시스템
│   ├── EducationSystem.ts   # 교육 (초등~대학, 수능, 전공)
│   ├── SocialSystem.ts      # 인간관계 (NPC, 호감도, 결혼)
│   ├── AssetSystem.ts       # 부동산/차량 자산 관리
│   ├── InvestmentSystem.ts  # 주식/예금 투자
│   ├── EventManager.ts      # 랜덤 이벤트 (선택지 분기)
│   ├── SuperpowerSystem.ts  # 초능력 해금/사용
│   ├── LicenseSystem.ts     # 자격증 공부/시험
│   ├── StressSystem.ts      # 스트레스/피로/번아웃
│   ├── MilitarySystem.ts    # 군 복무
│   ├── ChildSystem.ts       # 출산/양육
│   ├── RivalSystem.ts       # 라이벌 NPC
│   ├── LivingExpenseSystem.ts # 생활비/연금/보험
│   ├── EconomyEngine.ts     # 경기 순환 (호황/안정/불황)
│   ├── CharacterFactory.ts  # 캐릭터 생성 (이름/성별/가정환경)
│   ├── SaveManager.ts       # 세이브/로드 (localStorage)
│   ├── EventEmitter.ts      # 커스텀 이벤트 시스템
│   ├── types.ts             # 전체 타입 정의
│   └── data/                # 정적 데이터
│       ├── careers.ts       # 직업 데이터 (30+개)
│       ├── events.ts        # 이벤트 데이터 (100+개)
│       ├── licenses.ts      # 자격증 데이터
│       ├── properties.ts    # 부동산 데이터
│       ├── vehicles.ts      # 차량 데이터
│       ├── stocks.ts        # 투자 자산 데이터
│       ├── achievements.ts  # 업적 정의 (33개)
│       ├── actions.ts       # 사회 활동 데이터
│       ├── cities.ts        # 도시/대학 데이터
│       └── names.ts         # 이름 생성 데이터
├── renderer/         # 아이소메트릭 렌더링 (Canvas 2D)
│   ├── IsometricRenderer.ts # 메인 렌더러 (타일맵, 빌딩, 플레이어)
│   ├── Camera.ts            # 카메라 (줌, 패닝, 타겟 추적)
│   ├── mapData.ts           # 도시 맵 생성 (빌딩 배치)
│   └── types.ts             # 렌더러 타입 (ZoneType, Building 등)
├── components/       # React UI 컴포넌트
│   ├── GameCanvas.tsx       # Canvas 래퍼 (렌더러↔엔진 브릿지)
│   ├── TopBar.tsx           # 상단 HUD (날짜, 속도, 메뉴)
│   ├── StatsPanel.tsx       # 능력치 패널 (레벨+진행바+업적)
│   ├── BuildingPanel.tsx    # 건물 상호작용 (병원/체육관/은행 등)
│   ├── EventCard.tsx        # 이벤트 선택지 UI
│   ├── EventLog.tsx         # 이벤트 로그
│   ├── NPCPanel.tsx         # NPC 관계 패널
│   ├── InfancyOverlay.tsx   # 유아기 UI (활동 선택)
│   ├── MilitaryOverlay.tsx  # 군 복무 UI
│   ├── SuperpowerPanel.tsx  # 초능력 패널
│   ├── CheatConsole.tsx     # 치트 콘솔 (~키)
│   ├── SaveLoadMenu.tsx     # 세이브/로드 메뉴
│   └── LifeReport.tsx       # 사망 리포트 (인생 요약)
└── stores/
    └── gameStore.ts         # Zustand 글로벌 스토어
```

## 핵심 시스템

### 능력치 레벨링 (StatLevelSystem)

| 개념 | 설명 |
|------|------|
| **레벨 범위** | Lv.1 ~ Lv.999 (6가지 스탯: 건강/지능/매력/행복/사회성/체력) |
| **progress** | 0~100, 100 도달 시 레벨업 |
| **effectiveStat()** | `min(100, log2(level+1) * 14)` — 로그 곡선으로 0~100 환산 |
| **성장 확률** | `max(5%, 100% - level/200)` — 레벨 높을수록 실패 확률↑ |
| **감쇠** | `delta * max(0.1, 1 - level/300)` — 레벨 높을수록 획득량↓ |
| **하위 호환** | `stats[key] = progress` 동기화, 구세이브 자동 마이그레이션 |

```typescript
// 모든 스탯 변경은 이 함수를 통과
modifyStat(statLevels, stats, key, delta) → { leveledUp, newLevel }
// 읽기는 effectiveStat으로 환산
effectiveStat(sl: StatLevel) → 0~100
```

### 업적 시스템 (AchievementSystem)

33개 업적:
- **스탯 마일스톤** (24개): 각 스탯 Lv.10/25/50/100 달성
- **커리어** (3개): 첫 취업, 승진 3회, 연봉 1억
- **재산** (3개): 1억/10억/100억 순자산
- **소셜** (3개): 결혼, 자격증 3개, 부동산 3건

### 부모 재산 시스템

| 구분 | 빈곤 | 중산층 | 부유 |
|------|------|--------|------|
| 월 수입 | 200만 | 500만 | 1500만 |
| 투자 이벤트 | 5%/월 (60% 성공, 40% 실패) |
| 상속 | 부모 사망 또는 성인 시 |

### 아이소메트릭 렌더러

| 기능 | 설명 |
|------|------|
| **타일맵** | 64x32 다이아몬드 타일, 10개 존 타입 |
| **빌딩** | 3D 박스 렌더링, 클릭 상호작용 |
| **플레이어** | 픽셀아트 캐릭터, 12개 나이대별 외형 |
| **카메라** | 줌/패닝, 플레이어 추적 |
| **12 나이대** | 0-2(아기)/3-5(유아)/6-9(아동)/10-12(소년)/13-15(중학)/16-18(고교)/19-29(청년)/30-39(성인)/40-54(중년)/55-64(장년)/65-79(노년)/80+(고령) |
| **직업 악세서리** | 넥타이(사무직), 앞치마(요식업), 안전모(건설), 청진기(의료) |
| **재산 표현** | 부유할수록 의복 밝기 증가 |

### 게임 엔진 이벤트

```
dayPassed      → UI 상태 갱신
playerDied     → 사망 리포트 생성
levelUp        → 레벨업 로그
achievementUnlocked → 업적 알림
agePhaseChanged    → 인생 단계 전환
parentInvestment   → 부모 투자 성공
parentBankrupt     → 부모 투자 실패
inheritance        → 상속금
```

## 게임 흐름

```
캐릭터 생성 (이름/성별/가정환경)
  → 유아기 (0~6세): 활동 선택으로 기본 스탯 성장
  → 학생기 (7~18세): 자동 교육, 수능, 대학 진학
  → 청년기 (19~29세): 취업, 연애, 결혼
  → 성인기 (30~64세): 승진, 투자, 부동산, 자녀
  → 노년기 (65세+): 은퇴, 연금, 건강 관리
  → 사망 → 인생 리포트
```

## 특수 기능

| 기능 | 설명 |
|------|------|
| **치트 콘솔** | `~` 키로 열기. money/maxstats/level/skipto/age/immortal 등 |
| **나이 스킵** | `skipto <나이>` — 특정 나이까지 빠르게 진행 |
| **세이브/로드** | localStorage 기반, 3슬롯 + 자동저장 + 내보내기/가져오기 |
| **경기 순환** | 호황→안정→불황 사이클, 투자/부동산 가격에 영향 |
| **초능력** | 스탯 조건 충족 시 해금 (시간정지, 군중제어, 최면, 예지, 행운) |

## 데이터 구조

### Character (핵심 엔티티)

```typescript
interface Character {
  id: string
  name: string
  gender: 'male' | 'female'
  birthDate: GameDate
  stats: Stats           // { health, intelligence, charm, happiness, social, stamina }
  statLevels: StatLevels // { health: {level, progress}, ... } ← Lv.1~999
  achievements: string[] // 해금된 업적 ID 목록
  cash: number
  family: { wealth: 'poor'|'middle'|'rich', ... }
}
```

### GameState (전체 상태)

```typescript
interface GameState {
  player: Character
  npcs: Character[]
  date: GameDate         // { year, month, day }
  speed: TimeSpeed       // 'pause'|'normal'|'fast'|'faster'
  events: ActiveEvent[]  // 현재 활성 이벤트
}
```

## 엔진 시스템 간 연동

```
GameEngine.onDayTick()
  ├── TimeSystem.advanceDay()
  ├── StressSystem.tick()          → modifyStat() → 체력/행복 감소
  ├── SocialSystem.tick()          → modifyStat() → 행복 변동
  ├── CareerSystem.tick()          → effectiveStat() → 승진 판정
  ├── LicenseSystem.tick()         → effectiveStat() → 시험 점수
  ├── SuperpowerSystem.tick()      → effectiveStats() → 해금 체크
  ├── EventManager.tick()          → modifyPlayerStat() → 이벤트 효과
  ├── AchievementSystem.check()    → 매월 1일 업적 체크
  ├── 부모 월수입 + 투자           → 매월 1일 가족 재산 변동
  ├── 노화 (40세+)                → modifyPlayerStat() → 건강/체력 감소
  └── 사망 판정                    → statLevels.health.level <= 1 && progress <= 0
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 life-sim-rpg 레퍼런스를 보고
"판타지 인생 시뮬레이션"을 만들어줘.

스택: React 19 + TypeScript + Vite + Tailwind v4 + Zustand + Canvas 2D
- 아이소메트릭 맵 + 캐릭터 이동
- 능력치 레벨링 (Lv.1-999, 성장 확률 + 감쇠)
- 업적 시스템
- 직업/교육/결혼/투자
- 세이브/로드 (localStorage)
- 치트 콘솔
- 사망 시 인생 리포트

추가 요구:
- 마법/스킬 트리 추가
- 몬스터 전투 시스템
- 던전 탐험
```
