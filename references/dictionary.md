# dictionary - OpenStack CLI 위자드 V2

> GitHub: https://github.com/ganna40/dictionary

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 업무 도구 (CLI 레퍼런스 + 실행 + 커뮤니티) |
| **한줄 설명** | OpenStack/Linux CLI 사전 + 명령어 실행 + 시나리오 관리 + 커뮤니티 공유 |
| **타겟** | OpenStack 클라우드 인프라 관리자 |
| **테마** | 듀얼 (다크/라이트, CSS Variables) |
| **폰트** | 시스템 폰트 |

## 모듈 조합

```
Go (net/http) + MySQL + Vanilla JS SPA + CSS Variables + bcrypt
```

## 핵심 아키텍처

```
Go 바이너리 (cli-wizard.exe, 9.6MB)
  ├── 22개 REST API 엔드포인트
  ├── 9개 DB 테이블
  ├── 세션 기반 인증 (bcrypt + 쿠키)
  └── 내장 정적 파일 서빙 (go:embed)

프론트엔드 (index.html 단일 파일, 1,506줄)
  ├── 탭 기반 SPA (9개 섹션)
  ├── 하드코딩 기본 데이터 (50+ Linux, 40+ OpenStack 커맨드)
  ├── DB 데이터 오버레이 (사용자 커스텀 + 커뮤니티)
  └── 듀얼 테마 토글 (CSS Variables + localStorage)
```

## 9개 콘텐츠 섹션

| 탭 | 기능 |
|----|------|
| **OpenStack** | Nova/Neutron/Cinder/Glance/Keystone 5모듈 CLI 레퍼런스 |
| **Linux** | 50+ 리눅스 명령어 (파일, 시스템, 네트워크, 서비스, 패키지) |
| **즐겨찾기** | 자주 쓰는 명령어 저장 |
| **시나리오** | 변수 템플릿 + 단계별 워크플로우 |
| **팁** | 커뮤니티 공유 팁 (태그, 좋아요) |
| **가이드** | 상세 설정 가이드 (네트워크, 디스크, OS 설치) |
| **비교** | 레거시→신규 CLI 매핑 (nova list → openstack server list) |
| **마이그레이션** | 이전 버전 마이그레이션 가이드 |
| **트러블슈팅** | 에러 메시지→원인→해결방법 |

## 특수 기능

| 기능 | 설명 |
|------|------|
| **명령어 실행** | 브라우저에서 OpenStack CLI 직접 실행 (Go exec.Command) |
| **변수 템플릿** | 시나리오에 `{VM_NAME}` 같은 변수 → 실행 시 치환 |
| **듀얼 데이터** | 하드코딩 기본값 + DB 사용자 데이터 병합 |
| **공개/비공개** | is_public 플래그로 커뮤니티 공유 vs 개인 저장 |
| **레거시 매핑** | nova/cinder/neutron → 통합 openstack CLI 변환표 |
| **세션 인증** | bcrypt 해싱 + 7일 쿠키 세션 |
| **단일 바이너리** | Go embed로 정적 파일 내장, 9.6MB 실행 파일 하나 |
| **구문 하이라이팅** | CSS 기반 CLI 구문 색상 (.hl-cmd, .hl-opt, .hl-var) |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| Go 1.21 (net/http) | 백엔드 HTTP 서버 (프레임워크 없이) |
| MySQL/MariaDB | 9개 테이블 (사용자, 즐겨찾기, 시나리오, 팁 등) |
| bcrypt | 비밀번호 해싱 (cost=10) |
| go:embed | 정적 파일 바이너리 내장 |
| Vanilla JS | SPA 프론트엔드 (프레임워크 없이) |
| CSS Variables | 듀얼 테마 (다크/라이트) |
| exec.Command | OpenStack CLI 프로세스 실행 |

## DB 스키마 (9개 테이블)

```
users              — 사용자 (username, password_hash)
sessions           — 세션 (session_id, user_id, expires_at)
favorites          — 즐겨찾기 (name, command, category)
custom_scenarios   — 시나리오 (steps JSON, variables JSON, is_public)
tips               — 팁 (title, content, tags, likes, is_public)
compare_items      — 비교 (legacy_cmd, new_cmd)
migration_guides   — 마이그레이션 (old_cmd, new_cmd, tips JSON)
trouble_items      — 트러블슈팅 (error_msg, cause, solutions JSON)
linux_commands     — 리눅스 (category, name, command, example)
guides             — 가이드 (title, content JSON)
```

## 프로젝트 구조

```
dictionary/
└── cli-wizard-v2/
    ├── main.go          # Go 백엔드 (1,509줄, 22개 API)
    ├── go.mod           # Go 모듈 (mysql + bcrypt 의존성)
    ├── cli-wizard.exe   # 컴파일된 바이너리 (9.6MB)
    ├── static/
    │   └── index.html   # SPA 프론트엔드 (1,506줄)
    └── REPORT.md        # 프로젝트 문서
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 dictionary 레퍼런스를 보고
"인프라 CLI 사전 + 실행기"를 만들어줘.
Go (net/http) + MySQL + Vanilla JS SPA.
명령어 레퍼런스 + 브라우저 실행 + 시나리오 변수 템플릿.
세션 인증 (bcrypt) + 커뮤니티 공유 (is_public).
go:embed로 단일 바이너리 배포.
```
