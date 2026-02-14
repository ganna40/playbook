# [TWILIO] 전화/SMS 알림

> 긴급 알림이 필요할 때 사용. 텔레그램으로 부족하면 전화/SMS 추가.
> 의존: 없음 (TELEGRAM과 같이 쓰면 효과적)

## 필요 라이브러리

```bash
pip install twilio
```

## 환경 변수

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_FROM=+1xxxxxxxxxx    # Twilio 발신번호 (미국)
TWILIO_PHONE_TO=+82xxxxxxxxxx     # 수신번호 (한국 핸드폰)
```

> **주의**: Twilio 무료 계정은 **인증된 번호**로만 발신 가능. 유료 전환 시 아무 번호로 가능.

## 핵심 코드

### 전화 걸기 (한국어 TTS)

```python
from twilio.rest import Client
import os

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

def make_call(message: str):
    call = client.calls.create(
        twiml=f'<Response><Say language="ko-KR">{message}</Say></Response>',
        to=os.getenv("TWILIO_PHONE_TO"),
        from_=os.getenv("TWILIO_PHONE_FROM"),
    )
    return call.sid
```

### SMS 보내기

```python
def send_sms(message: str):
    msg = client.messages.create(
        body=message,
        to=os.getenv("TWILIO_PHONE_TO"),
        from_=os.getenv("TWILIO_PHONE_FROM"),
    )
    return msg.sid
```

### FastAPI와 조합

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/alert/call")
async def alert_call(message: str = "긴급 알림입니다"):
    sid = make_call(message)
    return {"status": "calling", "call_sid": sid}

@app.post("/alert/sms")
async def alert_sms(message: str = "긴급 알림입니다"):
    sid = send_sms(message)
    return {"status": "sent", "message_sid": sid}
```

## TwiML 옵션

```xml
<!-- 기본 한국어 음성 -->
<Response><Say language="ko-KR">서버가 다운되었습니다.</Say></Response>

<!-- 반복 재생 -->
<Response><Say language="ko-KR" loop="3">확인해주세요.</Say></Response>

<!-- 음성 + 키패드 입력 대기 -->
<Response>
  <Gather numDigits="1" action="/handle-key">
    <Say language="ko-KR">확인하시려면 1번을 눌러주세요.</Say>
  </Gather>
</Response>
```

## 주의사항

- **무료 계정 제한**: Trial 계정은 인증된 번호로만 발신. Console에서 번호 인증 필요
- **한국 번호 형식**: `+8210XXXXXXXX` (하이픈 없이, 국가코드 포함)
- **TTS 언어**: `language="ko-KR"`로 한국어 음성 합성
- **비용**: 전화 ~$0.013/분, SMS ~$0.0075/건 (미국 발신 기준)
- **발신번호**: Twilio에서 구매한 미국 번호 사용. 한국 번호 구매도 가능 (비쌈)
- **API 키 보안**: `.env`에만 저장, 절대 코드에 하드코딩 금지

## 사용 예시

```python
# TELEGRAM + TWILIO 조합 (telbot 패턴)
# 1차: 텔레그램 반복 알림
# 2차: 응답 없으면 전화
# 3차: 전화 안 받으면 SMS

async def escalate_alert(message: str):
    # 1단계: 텔레그램
    await send_telegram(message)
    await asyncio.sleep(60)

    if not confirmed:
        # 2단계: 전화
        make_call(message)
        await asyncio.sleep(120)

    if not confirmed:
        # 3단계: SMS
        send_sms(f"[미확인] {message}")
```
