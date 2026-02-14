# rackops - 데이터센터 인프라 관리 시스템 (DCIM)

> GitHub: https://github.com/ganna40/rackops

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 업무 도구 (DCIM — 데이터센터 인프라 관리) |
| **한줄 설명** | 물리 서버/GPU/네트워크 자산을 시각적으로 관리하고 실시간 모니터링하는 웹 기반 DCIM |
| **타겟** | 데이터센터 인프라 운영팀 |
| **테마** | 다크 (GitHub-inspired 팔레트) |
| **폰트** | 시스템 폰트 + D2Coding (모노) |

## 모듈 조합

```
React 19 + TypeScript + Vite 7 + Tailwind v4 + recharts
+ FastAPI + SQLAlchemy(async) + Alembic + PostgreSQL + Redis + Celery
+ JWT 인증 + WebSocket + i18n(ko/en)
```

## 핵심 아키텍처

```
[브라우저 — React 19 SPA]
    ↕ REST API (49개 엔드포인트) + WebSocket (실시간)
[FastAPI 백엔드]
    ├── SQLAlchemy 2.0 (async) + Alembic 마이그레이션
    ├── Celery (백그라운드 작업)
    ├── Redis (캐시 + 태스크 큐)
    └── JWT 인증 (HS256, 24시간)
         ↓
[PostgreSQL]
    ├── 인프라: datacenters, zones, racks, hosts, vms
    ├── 네트워크: network_devices, network_links
    ├── GPU: gpu_pools, gpu_devices, gpu_slices, gpu_allocations, gpu_tenant_quotas
    ├── 운영: alerts, event_logs, action_logs, audit_logs
    └── 설정: users, settings, integrations, notification_channels, incident_reports
```

## 주요 기능

| 기능 | 설명 |
|------|------|
| **비주얼 랙 다이어그램** | 가변 높이(42U/45U) 랙 시각화, 장비 위치 드래그&드롭 |
| **GPU MIG 관리** | GPU 풀/디바이스/슬라이스 할당, 테넌트 쿼타, 사용량 모니터링 |
| **인프라 액션** | Evacuate, IPMI Reboot/Power, Service Toggle, GPU Reset, Node Drain, VM Migrate |
| **실시간 대시보드** | KPI 카드, 크리티컬 이슈, 랙 맵, GPU 사용률, 이벤트 스트림 |
| **AI 인시던트 분석** | 장애 보고서 + AI 분석 필드 |
| **알림 채널** | 이메일, Slack 등 다중 알림 채널 |
| **감사 로그** | 접근/변경 감사 추적 (audit_logs) |
| **i18n** | React Context 기반 한국어/영어 전환 |
| **WebSocket** | 실시간 업데이트 |

## API 엔드포인트 (49개)

| 그룹 | 주요 엔드포인트 |
|------|----------------|
| **Auth** | POST login, register, refresh / GET me |
| **Dashboard** | GET kpis, critical-issues, rack-map, gpu-utilization, events |
| **Infra** | GET/PATCH datacenters, racks, hosts, vms, zones |
| **GPU** | GET/POST pools, slices, nodes, tenant-allocation / DELETE slices |
| **Actions** | POST evacuate, ipmi/reboot, ipmi/power, service/toggle, gpu/reset, node/drain, vm/migrate |
| **Alerts** | GET / PATCH |
| **Events** | GET |
| **Settings** | GET |
| **WebSocket** | /ws |
| **Health** | GET /api/health |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| React 19 + TypeScript | SPA 프론트엔드 |
| Tailwind CSS v4 | 다크 테마 스타일링 (@theme 블록) |
| Vite 7 | 빌드 + 개발 서버 + API 프록시 |
| recharts | 차트 (GPU 사용률, KPI 등) |
| lucide-react | 아이콘 팩 |
| react-router-dom 7 | SPA 라우팅 |
| FastAPI | 비동기 REST API + WebSocket |
| SQLAlchemy 2.0 (async) | ORM (asyncpg 드라이버) |
| Alembic | DB 마이그레이션 |
| PostgreSQL | 메인 DB (20+ 테이블) |
| Redis 5 | 캐시 + Celery 브로커 |
| Celery 5 | 백그라운드 작업 (모니터링 등) |
| python-jose | JWT 토큰 (HS256) |
| passlib[bcrypt] | 비밀번호 해싱 |
| Pydantic v2 | 요청/응답 모델 검증 |
| websockets | 실시간 업데이트 |

## DB 스키마 (20+ 테이블)

```
인프라:
  datacenters → zones → racks → hosts → vms
                                  └→ gpu_devices → gpu_slices

네트워크:
  network_devices, network_links

GPU 관리:
  gpu_pools, gpu_devices, gpu_slices, gpu_allocations, gpu_tenant_quotas

운영:
  alerts, event_logs, action_logs, audit_logs, incident_reports

설정:
  users (admin/operator/viewer), settings, integrations, notification_channels
```

## 프론트엔드 페이지

| 페이지 | 기능 |
|--------|------|
| **Dashboard** | KPI 카드 + 크리티컬 이슈 + 랙 맵 + GPU 사용률 + 이벤트 |
| **GPU Management** | 풀 관리 + 노드 GPU 상태 + 슬라이스 할당 |
| **Actions** | 인프라 액션 (reboot, power, migration, evacuation) |
| **AI Insights** | 인시던트 분석 + 추천 |
| **Settings** | 시스템 설정 + 통합 |

## 프로젝트 구조

```
Rackopt/
├── backend/
│   ├── main.py            # FastAPI 진입점 (49개 엔드포인트)
│   ├── requirements.txt   # FastAPI, SQLAlchemy, Redis, Celery, JWT 등
│   └── ...
├── rackops/               # React 프론트엔드
│   ├── src/
│   │   ├── App.tsx        # 메인 SPA + 라우팅
│   │   ├── pages/         # Dashboard, GPU, Actions, AI, Settings
│   │   ├── components/    # 공통 컴포넌트
│   │   └── i18n/          # 한국어/영어 번역
│   ├── package.json       # React 19, Vite 7, Tailwind v4
│   └── index.html
└── .gitignore
```

## 마스터 프롬프트 (AI 복원용)

아래 프롬프트를 AI에게 던지면 이 프로젝트의 핵심을 처음부터 재구성 가능:

```
당신은 숙련된 풀스택 개발자입니다.
데이터센터 자산 관리 시스템 'RackOps'를 구축해주세요.

기술 스택:
- Backend: FastAPI + SQLAlchemy(async) + PostgreSQL + Redis + Celery + JWT
- Frontend: React 19 + TypeScript + Vite 7 + Tailwind v4 + recharts

핵심 기능:
1. 비주얼 랙 다이어그램 (가변 U높이, 드래그&드롭)
2. GPU MIG 슬라이싱 (풀/디바이스/슬라이스/할당/테넌트 쿼타)
3. 인프라 액션 (Evacuate, IPMI Reboot/Power, VM Migrate, Node Drain)
4. 실시간 대시보드 (KPI, 랙 맵, GPU 사용률, 이벤트)
5. AI 인시던트 분석
6. 감사 로그 + 다중 알림 채널
7. i18n (한국어/영어)
8. WebSocket 실시간 업데이트

DB: 20+ 테이블 (인프라 + GPU + 운영 + 설정)
API: 49개 REST 엔드포인트 + WebSocket
인증: JWT (HS256, 24시간) + 역할 (admin/operator/viewer)
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 rackops 레퍼런스를 보고
"데이터센터 인프라 관리 시스템"을 만들어줘.
React 19 + TypeScript + Vite + Tailwind v4 (프론트)
+ FastAPI + SQLAlchemy + PostgreSQL + Redis (백엔드).
랙 시각화 + GPU 관리 + 인프라 액션 + 실시간 대시보드.
JWT 인증 + WebSocket + i18n(ko/en).
```
