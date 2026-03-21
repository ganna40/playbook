# OpsCommand Builder - CLI 명령어 자동생성기

> GitHub: https://github.com/ganna40/opscommand-builder
> 로컬: C:\Users\ganna\opscommand-builder

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | CLI 명령어 빌더 (운영 도구) |
| **한줄 설명** | OpenStack/OpenShift 행위를 검색하면 옵션 선택만으로 CLI 명령어가 자동 완성되는 웹앱 |
| **타겟** | 클라우드 인프라 운영자 (RHOSP, Helion Legacy, OCP 환경) |
| **테마** | 라이트 (네이비 텍스트 + 상태색 기반) |
| **폰트** | Pretendard + JetBrains Mono (시스템 fallback) |

## 모듈 조합

```
React19 + TypeScript + Vite + TailwindV4 + Zustand + Fuse.js + Vitest
```

## 핵심 아키텍처

| 레이어 | 역할 |
|--------|------|
| **CommandSchema (JSON)** | 101개 명령어 데이터 (profile별 binary/template/flag 분기) |
| **schemaResolver** | profile + role → effective schema 변환 |
| **ruleEngine** | required/depends_on/conflicts/one_of/min-max/danger 검증 |
| **escapeEngine** | bash/powershell/fish 쉘별 안전한 값 이스케이프 |
| **templateRenderer** | token 조합 → 최종 명령어 문자열 생성 |
| **previewPipeline** | resolver → validator → renderer 오케스트레이터 |
| **searchEngine** | Fuse.js + 동의어 확장 검색 |
| **Workspace** | 작업 기록 저장/수정/삭제/순서변경/일괄복사 (localStorage persist) |

## 특수 기능

| 기능 | 설명 |
|------|------|
| **Profile 분기** | rhosp-17 vs helion-legacy, ocp-4.x vs ocp-3.x에 따라 binary/flag/template 자동 전환 |
| **레거시 바이너리** | nova, neutron, cinder, swift, keystone, heat, glance 모두 helion-legacy로 지원 |
| **Danger UX** | 파괴적 명령은 confirm 없이 복사 불가 |
| **keyvalue escaping** | KEY='value with spaces' 형태로 값만 이스케이프 |
| **value_transform_by_profile** | 프로파일별 placeholder 자동 전환 (project name vs tenant-id) |
| **Workspace** | 만든 명령어를 저장해두고 Runbook처럼 순서대로 관리/일괄복사 |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| **Zustand 5 (persist)** | 앱 상태 + Workspace localStorage 영속 |
| **Fuse.js** | 한/영 혼합 fuzzy 검색 + 동의어 확장 |
| **Vitest** | 69개 테스트 (엔진 단위 + 통합 검증) |
| **Tailwind CSS v4 (@theme)** | 커스텀 컬러 (navy, accent, danger, warning, success) |

## 데이터 구조

```
src/data/commands/
├── openstack-compute.ts      # 15개 (nova)
├── openstack-network.ts      # 15개 (neutron)
├── openstack-floatingip.ts   # 6개 (nova/neutron)
├── openstack-quota-image.ts  # 5개 (nova/glance)
├── openstack-node.ts         # 6개 (nova)
├── openstack-volume.ts       # 12개 (cinder) — retype 포함
├── openstack-storage.ts      # 7개 (swift)
├── openstack-identity.ts     # 9개 (keystone)
├── openstack-orchestration.ts # 5개 (heat)
├── openshift-apps.ts         # 10개 (oc)
├── openshift-build.ts        # 5개 (oc)
└── openshift-node.ts         # 6개 (oc)
총 101개 명령어
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 opscommand-builder 레퍼런스를 보고
"AWS CLI Command Builder"를 만들어줘.
스키마 기반 명령어 생성 아키텍처 동일.
profile을 AWS region으로, platform을 AWS service로 매핑.
```
