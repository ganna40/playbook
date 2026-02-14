# telbot - 텔레그램 트리거 알림 봇

> URL: (내부 서비스)
> GitHub: https://github.com/ganna40/telbot

## 개요

| 항목 | 내용 |
|------|------|
| **유형** | 알림 봇 (반복 알림 + 확인 시스템) |
| **한줄 설명** | 이벤트 발생 → 텔레그램 반복 알림 → 확인 누를 때까지 안 멈춤 |
| **타겟** | 서버 모니터링, 긴급 알림이 필요한 상황 |
| **테마** | - (봇이 UI) |
| **폰트** | - |

## 모듈 조합

```
TELEGRAM + TWILIO + FastAPI
```

## 핵심 아키텍처

```
외부 시스템 → POST /trigger (message, interval)
                 ↓
           alert_id 발급 (UUID 8자리)
                 ↓
           텔레그램 반복 전송 (🚨 [1] 메시지, 🚨 [2] 메시지, ...)
                 ↓
           사용자가 "✅ 확인" 버튼 클릭
                 ↓
           알림 중지 + 결과 반환 (총 전송 수)
```

## API 엔드포인트

| 메서드 | 경로 | 기능 |
|--------|------|------|
| POST | `/trigger` | 반복 알림 시작 (message, interval, chat_id) |
| POST | `/telegram` | 단발 메시지 전송 |
| GET | `/stop/{alert_id}` | API로 알림 중지 |
| GET | `/health` | 상태 확인 (활성 알림 수) |
| GET | `/get-chat-id` | 텔레그램 chat_id 조회 |

## 특수 기능

| 기능 | 설명 |
|------|------|
| **반복 알림** | 0.5~10초 간격으로 확인할 때까지 반복 |
| **인라인 확인 버튼** | 텔레그램 InlineKeyboard로 "✅ 확인" 버튼 |
| **Twilio 음성/SMS** | 전화 통화(한국어 TTS) + SMS 발송 가능 |
| **다중 알림 동시 관리** | UUID 기반 alert_id로 여러 알림 독립 관리 |
| **상태 모니터링** | `/health` 엔드포인트로 활성 알림 수 확인 |

## 핵심 API/기술

| 기술 | 용도 |
|------|------|
| FastAPI | REST API 서버 |
| python-telegram-bot 20+ | 텔레그램 메시지 + 콜백 버튼 |
| Twilio SDK | 음성 전화 (한국어 TTS) + SMS |
| Pydantic | 요청 모델 검증 |
| asyncio | 비동기 반복 알림 루프 |

## 핵심 코드 패턴

### 반복 알림 + 확인 버튼
```python
active_alerts: dict[str, bool] = {}  # 인메모리 상태

@app.post("/trigger")
async def trigger_alert(req: TriggerRequest):
    alert_id = str(uuid.uuid4())[:8]
    active_alerts[alert_id] = True

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ 확인", callback_data=alert_id)]
    ])

    count = 0
    while active_alerts.get(alert_id, False):
        count += 1
        await bot.send_message(
            chat_id=chat_id,
            text=f"🚨 [{count}] {req.message}",
            reply_markup=keyboard
        )
        await asyncio.sleep(req.interval)

    del active_alerts[alert_id]
    return {"alert_id": alert_id, "total_sent": count, "status": "stopped"}
```

### 콜백 핸들러 (확인 처리)
```python
async def callback_handler(update: Update, context):
    alert_id = update.callback_query.data
    if alert_id in active_alerts:
        active_alerts[alert_id] = False  # 루프 중지
        await update.callback_query.answer("알림 중지됨!")
```

### Twilio 전화 (한국어 TTS)
```python
call = client.calls.create(
    twiml='<Response><Say language="ko-KR">긴급 알림입니다.</Say></Response>',
    to=phone_to,
    from_=phone_from,
)
```

## 데이터 구조

```
상태 관리: 인메모리 dict (active_alerts)
├── alert_id (UUID 8자리) → True/False (활성/비활성)
└── 서버 재시작 시 초기화 (DB 없음)
```

## 프로젝트 구조

```
telbot/
├── app.py              # FastAPI 메인 (엔드포인트 + 봇)
├── requirements.txt    # twilio, python-telegram-bot, fastapi, uvicorn
├── .env               # ★ 민감정보 (Twilio SID/Token, Bot Token)
├── test_trigger.py    # 통합 테스트
├── test_burst.py      # 반복 알림 데모
├── test_sms.py        # SMS 테스트
└── test_call_debug.py # 전화 테스트
```

## AI에게 비슷한 거 만들게 하려면

```
playbook의 telbot 레퍼런스를 보고
"서버 모니터링 알림봇"을 만들어줘.
TELEGRAM + TWILIO 조합.
FastAPI로 API 서버 만들고,
POST /trigger로 알림 시작하면 확인 누를 때까지 반복.
Twilio로 전화/SMS 알림도 추가.
```
