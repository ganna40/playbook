# rackops - 데이터센터 시각화 및 자동화 관리 시스템 (DCIM)

> GitHub: https://github.com/ganna40/rackops

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 업무 도구 (DCIM — 데이터센터 인프라 관리) |
| **한줄 설명** | 물리 서버/네트워크 자산을 시각적으로 관리하고 SSH/SNMP로 실시간 모니터링하는 웹 기반 DCIM |
| **타겟** | 데이터센터 인프라 운영팀 |
| **테마** | 다크 |

## 모듈 조합

```
Svelte (Vite) + Tailwind CSS + D3.js + Lucide-Svelte
+ FastAPI + APScheduler + Paramiko (SSH) + PySNMP (SNMP) + OpenPyXL
+ MySQL
```

## 핵심 아키텍처

```
[브라우저 — Svelte SPA]
    ↕ REST API
[FastAPI 백엔드]
    ├── CRUD API (위치, 랙, 장비)
    ├── APScheduler (1분마다 상태 폴링)
    ├── monitor.py (SSH/SNMP 수집)
    │     ├── Paramiko → ipmitool, ip link (전력/온도/인터페이스)
    │     └── PySNMP → iLO/IPMI (모델명, 시리얼)
    └── OpenPyXL (비주얼 엑셀 리포트)
         ↓
[MySQL]
    ├── locations (위치)
    ├── racks (랙, 가변 U높이)
    └── physical_devices (자산+접속+상태 JSON)
```

## 기술 스택

| 구분 | 기술 | 설명 |
|------|------|------|
| **Frontend** | Svelte (Vite) | 반응형 웹 UI, 컴포넌트 기반 |
| | Tailwind CSS | 유틸리티 퍼스트 CSS |
| | D3.js | 네트워크 토폴로지 시각화 (Force-Directed Graph) |
| | Lucide-Svelte | UI 아이콘 팩 |
| **Backend** | FastAPI | 비동기 REST API |
| | Uvicorn | ASGI 웹 서버 |
| | APScheduler | 백그라운드 주기적 모니터링 스케줄러 |
| | Paramiko | SSH 클라이언트 (서버 원격 접속 및 명령어 실행) |
| | PySNMP | SNMP 클라이언트 (iLO/IPMI 정보 수집) |
| | OpenPyXL | 엑셀 스타일링 및 비주얼 리포트 생성 |
| **Database** | MySQL | 자산, 위치, 랙, 케이블링 정보 |

## 주요 기능

| 기능 | 설명 |
|------|------|
| **비주얼 랙 다이어그램** | 가변 높이(42U/45U) 랙 시각화, 드래그&드롭 장비 이동, PDU 자동 렌더링, 상태 LED |
| **실시간 모니터링** | SSH/SNMP로 전력(Watt)/온도(Temp)/인터페이스 상태 자동 수집, 1분 주기 폴링 |
| **Auto-Detect** | IP/ID/PW 입력만으로 SSH/SNMP 접속 → 모델명/시리얼 자동 수집 |
| **네트워크 토폴로지** | D3.js Force Graph로 장비 간 연결 관계(Uplink) 시각화, 줌/팬/드래그 |
| **SSH Console** | 웹 UI에서 서버에 SSH 명령어 전송 및 결과 확인 |
| **비주얼 엑셀 리포트** | 실제 랙 모양으로 셀 병합 + 색상 처리, 위치/랙별 필터링 |

## DB 스키마

```
locations: id, name, width, height

racks: id, name, location_id, total_u (기본 42, 가변)

physical_devices:
  기본정보: id, name, type, status, rack_id, start_u, u_height
  자산정보: manufacturer, model_name, serial_number, asset_tag, purchase_date
  접속정보: management_ip, ssh_user, ssh_password, ssh_port, ilo_ip, snmp_community
  상태데이터(JSON): specs (cpu_temp, power_watt 등), network_info
```

## 프론트엔드 컴포넌트

| 컴포넌트 | 기능 |
|----------|------|
| **App.svelte** | 메인 UI, 모달, 탭 관리, 비즈니스 로직 |
| **Rack.svelte** | 랙 시각화 (가변 U, PDU, 드래그&드롭, 상태 LED) |
| **Topology.svelte** | D3.js 네트워크 토폴로지 (Force Graph) |
| **store.js** | 전역 상태 관리 + API 호출 함수 |

## 프로젝트 구조

```
RackOps/
├── backend/
│   ├── main.py            # API 서버 진입점, 스케줄러, 엔드포인트
│   ├── monitor.py         # SSH/SNMP 수집 로직 (Paramiko, PySNMP)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── Rack.svelte      # 랙 시각화 컴포넌트
│   │   │   ├── Topology.svelte  # 네트워크 토폴로지
│   │   │   └── store.js         # 전역 상태 관리
│   │   ├── App.svelte           # 메인 UI
│   │   └── main.js
│   ├── package.json
│   └── index.html
└── .gitignore
```

## 마스터 프롬프트 (AI 복원용)

아래 프롬프트를 AI에게 던지면 이 프로젝트의 핵심을 처음부터 재구성 가능:

```
당신은 숙련된 풀스택 개발자입니다.
데이터센터 자산 관리 시스템 'RackOps'를 구축해주세요.

기술 스택:
- Backend: FastAPI, Uvicorn, APScheduler, MySQL Connector
- Frontend: Svelte (Vite), Tailwind CSS, Lucide Icons, D3.js
- Utilities: Paramiko (SSH), PySNMP (SNMP), OpenPyXL (Excel)

DB 스키마:
- locations: id, name, width, height
- racks: id, name, location_id, total_u (가변)
- physical_devices: 기본정보 + 자산정보 + 접속정보(IP/SSH/iLO) + 상태JSON

핵심 기능:
1. 비주얼 랙 다이어그램 (가변 U높이, 드래그&드롭, PDU 자동 렌더링)
2. SSH/SNMP 실시간 모니터링 (APScheduler 1분 폴링, 전력/온도/인터페이스)
3. Auto-Detect (IP/ID/PW → 모델명/시리얼 자동 수집)
4. 네트워크 토폴로지 (D3.js Force Graph)
5. SSH Console (웹에서 명령어 실행)
6. 비주얼 엑셀 리포트 (셀 병합 + 색상, 필터링)
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 rackops 레퍼런스를 보고
"데이터센터 인프라 관리 시스템"을 만들어줘.
Svelte + Vite + Tailwind + D3.js (프론트)
+ FastAPI + Paramiko + PySNMP + MySQL (백엔드).
랙 시각화 + SSH/SNMP 모니터링 + 네트워크 토폴로지 + 비주얼 엑셀.
```
