# collab-tool - 팀 협업 대시보드 (ARK-CORTEX)

> URL: (내부 서비스)
> GitHub: https://github.com/ganna40/my_collaboration_tool

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 업무 도구 (팀 태스크 + KPI + 캘린더 + 지식창고) |
| **한줄 설명** | JARVIS 스타일 팀 협업 대시보드. 태스크 관리 + KPI 추적 + 캘린더 + 지식 창고 |
| **타겟** | 팀 내부 업무 관리 |
| **테마** | 듀얼 (다크: JARVIS 네온 / 라이트: 클린) |
| **폰트** | Orbitron (제목) + Noto Sans KR (본문) |

## 모듈 조합

```
Flask + POCKETBASE + Bootstrap 5 + Glassmorphism + Chart.js + FullCalendar
```

## 핵심 아키텍처

```
Flask 앱 (5개 Blueprint)
  ├── /tasks       → 태스크 CRUD + Excel 내보내기 + 파일 첨부
  ├── /calendar    → FullCalendar + 우선순위 색상 코딩
  ├── /kpi         → 가중 KR + Burn-up 차트 + 태스크 연결
  ├── /completed   → 완료 아카이브 + 복원
  └── /warehouse   → 지식 카테고리 + 다중 파일 업로드
       ↓
  PocketBase (BaaS)
  ├── users        → 인증 + 세션
  ├── tasks        → 태스크 데이터 + 관계
  ├── kpis         → OKR 목표
  ├── kpi_items    → 핵심 결과 (가중치)
  ├── kpi_history  → 진행률 이력 (Burn-up)
  ├── kpi_logs     → 활동 로그
  └── warehouse    → 지식 문서 + 첨부파일
```

## 특수 기능

| 기능 | 설명 |
|------|------|
| **Glassmorphism UI** | backdrop-filter: blur(12px) + 투명 배경 + 네온 글로우 |
| **JARVIS 배경** | 3개 회전 원형 + 그리드 오버레이 애니메이션 |
| **KPI 가중 평균** | 핵심 결과(KR)에 가중치 부여 → 가중 평균으로 KPI 진행률 자동 계산 |
| **Burn-up 차트** | Chart.js 라인 차트로 KPI 진행 추세 시각화 |
| **On-Track 분석** | 시간 대비 진행률 갭 분석 (ON TRACK / AT RISK / OFF TRACK) |
| **태스크-KPI 연결** | 태스크를 KPI 핵심 결과에 링크/언링크 |
| **FullCalendar** | 우선순위별 색상 코딩 (빨강=긴급, 노랑=중요, 초록=일반) |
| **Excel 내보내기** | pandas + openpyxl로 업무 목록 Excel 다운로드 |
| **다중 파일 업로드** | PocketBase API로 여러 파일 동시 첨부 |
| **듀얼 테마** | localStorage 기반 다크/라이트 전환 + CSS Variables |
| **세션 인증** | PocketBase 토큰 기반 + Flask 세션 (1시간) |
| **페이지 로더** | JARVIS 스타일 로딩 바 + 상태 텍스트 |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| Flask + Blueprint | 웹 프레임워크 + 모듈 라우팅 |
| PocketBase | BaaS (DB + 인증 + 파일 + REST API) |
| Bootstrap 5 | UI 프레임워크 |
| Chart.js | Burn-up 라인 차트 |
| FullCalendar 6 | 캘린더 뷰 (월/주/리스트) |
| pandas + openpyxl | Excel 파일 생성/내보내기 |
| Glassmorphism CSS | 블러 + 투명 + 네온 UI |
| Orbitron 폰트 | SF 스타일 제목 폰트 |

## KPI 가중 평균 계산

```python
def recalculate_kpi_progress(kpi_id):
    items = pb.collection('kpi_items').get_full_list(
        query_params={'filter': f'kpi="{kpi_id}"'}
    )
    total_weight = 0
    weighted_sum = 0
    for item in items:
        w = item.weight if item.weight > 0 else 1
        p = item.progress if item.progress else 0
        total_weight += w
        weighted_sum += (p * w)

    final = int(weighted_sum / total_weight) if total_weight > 0 else 0
    pb.collection('kpis').update(kpi_id, {
        "progress": final,
        "status": "achieved" if final >= 100 else "ongoing"
    })
```

## Glassmorphism CSS 핵심

```css
:root {
    --card-bg: rgba(255, 255, 255, 0.75);
}
[data-theme="dark"] {
    --primary-color: #00a8ff;
    --card-bg: rgba(16, 28, 45, 0.6);
}

.glass-effect {
    background-color: var(--card-bg) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
}
```

## PocketBase 연동 패턴

```python
from pocketbase import PocketBase

pb = PocketBase('http://127.0.0.1:8090')

# 인증
auth = pb.collection('users').auth_with_password(email, password)

# CRUD
tasks = pb.collection('tasks').get_full_list(
    query_params={'filter': 'status != "completed"', 'expand': 'assignee'}
)
pb.collection('tasks').create({"title": "...", "priority": "urgent"})
pb.collection('tasks').update(task_id, {"status": "completed"})
pb.collection('tasks').delete(task_id)
```

## 프로젝트 구조

```
my_collaboration_tool/
├── app.py                    # Flask 메인 (Blueprint 등록 + 인증)
├── config.py                 # PocketBase URL, 세션 설정
├── requirements.txt          # flask, pocketbase, pandas, openpyxl, requests
├── services/
│   └── pb_service.py        # PocketBase 싱글톤
├── views/
│   ├── task_views.py        # 태스크 CRUD + Excel 내보내기
│   ├── calendar_views.py    # FullCalendar 이벤트
│   ├── kpi_views.py         # KPI + 가중 계산 + Burn-up
│   ├── completed_views.py   # 완료 아카이브
│   └── warehouse_views.py   # 지식 창고
├── templates/
│   ├── base.html            # 네비, JARVIS 배경, 테마 토글
│   ├── task_list.html       # 태스크 카드 그리드
│   ├── calendar.html        # FullCalendar 뷰
│   ├── kpi_detail.html      # Chart.js Burn-up
│   └── warehouse_list.html  # 지식 카드 그리드
└── static/
    ├── css/style.css        # Glassmorphism + 듀얼 테마
    └── js/loader.js         # JARVIS 로딩 애니메이션
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 collab-tool 레퍼런스를 보고
"팀 프로젝트 관리 도구"를 만들어줘.
Flask + POCKETBASE 조합.
태스크 CRUD + KPI 가중 평균 + FullCalendar + 지식 창고.
Glassmorphism 다크 테마로.
Excel 내보내기, 파일 업로드 포함.
```
