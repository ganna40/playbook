# error-automation - SRE 장애 보고서 자동화 봇

> GitHub: https://github.com/ganna40/error_automation

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | AI 챗봇 + 알림 봇 (SRE 장애 대응 자동화) |
| **한줄 설명** | 장애 발생 → AI가 보고서 자동 생성 → 텔레그램으로 전달 → 자연어로 수정 → 에스컬레이션 |
| **타겟** | SRE/인프라 운영팀 |
| **테마** | - (텔레그램 봇) |
| **폰트** | - |

## 모듈 조합

```
LLM + TELEGRAM + TWILIO + SQLite + FastAPI
```

## 핵심 아키텍처

```
장애 알림 수신
    ↓
IncidentManager → LLM(gemma3:4b)으로 보고서 자동 생성
    ↓
3단계 보고서 라이프사이클:
  ① 발생보고 → ② 경과보고 → ③ 종료보고
    ↓
자연어 수정: "영향도를 VM 5대로 바꿔"
    ↓
에스컬레이션: 텔레그램 DM → 전화(Twilio) → 다음 당직자
    ↓
"보고서 확정" → 인시던트 종료
```

## 3단계 보고서 라이프사이클

```
[발생보고 v1] ← LLM 자동 생성 (알림 데이터 + 유사 사례 참조)
      ↓ 자연어 수정 ("원인을 CPU Fault로 바꿔")
[발생보고 v2] ← LLM이 필드 수정
      ↓ "경과보고 작성해줘"
[경과보고 v1] ← LLM이 이전 보고서 전체 참조 + 현재 시각 반영
      ↓ "종료보고 작성해줘"
[종료보고 v1] ← LLM이 전체 보고서 + 최종 원인/영향 반영
      ↓ "보고서 확정"
[인시던트 종료] ← is_confirmed=1, status='closed'
```

## 특수 기능

| 기능 | 설명 |
|------|------|
| **LLM 보고서 자동 생성** | Ollama(gemma3:4b)로 장애 알림 → 구조화된 보고서 |
| **자연어 수정** | "영향도를 VM 5대로 바꿔" → 키워드 매칭(영향도/원인/조치) → LLM 수정 |
| **3단계 보고서** | 발생보고 → 경과보고 → 종료보고, 각 단계 버전 관리 |
| **에스컬레이션** | 당직자 Tier별 순차: 텔레그램 DM → Twilio 전화 → 다음 당직자 |
| **당직 관리** | /oncall add/remove/list/clear로 당직자 관리 |
| **유사 사례 참조** | 보고서 생성 시 과거 유사 인시던트 근본원인+해결방안 주입 |
| **리소스 모니터링** | psutil로 Ollama 프로세스 CPU/메모리/GPU 사용량 추적 |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| python-telegram-bot 20+ | 텔레그램 봇 (커맨드 + 인라인 버튼 + 콜백) |
| Ollama (gemma3:4b) | 보고서 생성/수정 (로컬 LLM) |
| Twilio SDK | 에스컬레이션 전화 (한국어 TTS) |
| SQLite3 | 인시던트/보고서/알림/당직 DB |
| FastAPI | 웹훅 API (선택사항) |
| httpx | Ollama 비동기 HTTP 호출 |
| psutil | LLM 프로세스 리소스 모니터링 |
| pytest | 비동기 테스트 (모킹) |

## 텔레그램 커맨드

| 커맨드 | 기능 |
|--------|------|
| `/start` | 환영 메시지 + 채팅 ID 표시 |
| `/help` | 사용 가능한 커맨드 목록 |
| `/test` | 테스트 알림 시뮬레이션 → 보고서 생성 → 에스컬레이션 |
| `/status` | 활성 인시던트 상태 |
| `/oncall list` | 당직자 목록 |
| `/oncall add 이름 텔레그램ID 전화번호` | 당직자 추가 |
| `/oncall remove 텔레그램ID` | 당직자 제거 |

## 자연어 메시지 처리

| 메시지 | 동작 |
|--------|------|
| "경과보고 작성해줘" | 경과보고 생성 |
| "종료보고 작성해줘" | 종료보고 생성 |
| "보고서 확정" | 인시던트 종료 |
| "현재 보고서" | 최신 보고서 표시 |
| "영향도를 ○○로 바꿔" | 필드 수정 (영향도/원인/조치) |

## DB 스키마

```
incidents           — 인시던트 (id, status, stage, alert_data)
incident_reports    — 보고서 (type, version, title, impact, cause, actions)
incident_conversations — 대화 이력 (message, bot_response, action_type)
alert_history       — 알림 이력 (status, acknowledged_by, channel)
on_call_schedule    — 당직 명단 (name, telegram_id, phone, tier)
```

## 프로젝트 구조

```
error_automation/
├── run_telegram_bot.py              # 메인 봇 진입점 (폴링)
├── run_test.py                      # 시나리오 테스트 + 리소스 모니터링
├── run_incident_test.py             # 3단계 보고서 인터랙티브 테스트
├── trigger_alert.py                 # CLI 알림 시뮬레이터
├── config.py                        # ★ 인증 정보 (환경변수로 이전 필요)
├── requirements.txt
├── app/
│   ├── database/models.py           # SQLite CRUD (IncidentDB)
│   └── services/
│       ├── incident_manager.py      # 비즈니스 로직 (라이프사이클)
│       ├── incident_report_generator.py  # LLM 보고서 생성
│       ├── telegram_urgent_alert.py     # 에스컬레이션 오케스트레이터
│       └── twilio_call_service.py       # Twilio 전화 서비스
├── data/incidents.db                # SQLite DB (자동 생성)
└── tests/                           # pytest 비동기 테스트
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 error-automation 레퍼런스를 보고
"SRE 장애 자동 보고서 시스템"을 만들어줘.
LLM + TELEGRAM + TWILIO 조합.
3단계 보고서 (발생→경과→종료) + 자연어 수정.
에스컬레이션: 텔레그램 → 전화 → 다음 당직자.
SQLite로 인시던트/보고서/당직 관리.
```
