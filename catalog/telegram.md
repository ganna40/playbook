# [TELEGRAM] 텔레그램 봇 연동 (python-telegram-bot)

> 텔레그램 메신저로 AI 봇 서비스를 제공할 때 사용.
> 의존: 없음 (백엔드 API와 조합 권장)
> psycho-bot에서 사용.

## 필요 라이브러리

```bash
pip install python-telegram-bot==21.0
```

## BotFather로 봇 생성

```
1. 텔레그램에서 @BotFather 검색
2. /newbot 명령
3. 봇 이름 입력 (예: 마음벗)
4. 봇 username 입력 (예: mindmate_bot)
5. 토큰 받기 → .env에 저장
```

```bash
# .env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

## 기본 봇 구조

```python
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)
import httpx

TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
API_BASE_URL = "http://localhost:8000"  # FastAPI 서버

# 세션 관리
user_sessions: dict[int, str] = {}  # telegram_user_id → session_id

# === 커맨드 핸들러 ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """봇 시작 - /start"""
    user = update.effective_user
    user_sessions[user.id] = f"tg_{user.id}"

    await update.message.reply_text(
        f"안녕하세요 {user.first_name}님! 😊\n"
        "무엇이든 편하게 이야기해주세요."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """도움말 - /help"""
    await update.message.reply_text(
        "/start - 대화 시작\n"
        "/reset - 대화 초기화\n"
        "/help  - 도움말"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """대화 초기화 - /reset"""
    user_id = update.effective_user.id
    user_sessions.pop(user_id, None)
    await update.message.reply_text("대화가 초기화되었습니다.")

# === 메시지 핸들러 ===

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """일반 텍스트 메시지 처리"""
    user = update.effective_user
    message = update.message.text

    # 세션 확인
    session_id = user_sessions.get(user.id, f"tg_{user.id}")
    user_sessions[user.id] = session_id

    # 타이핑 표시
    await update.message.chat.send_action("typing")

    # 백엔드 API 호출
    response_text = await send_to_api(
        session_id=session_id,
        message=message,
        user_id=f"telegram_{user.id}",
        user_name=user.first_name,
    )

    # 텔레그램 메시지 길이 제한 (4096자)
    if len(response_text) > 4000:
        response_text = response_text[:4000] + "..."

    await update.message.reply_text(response_text)

# === API 호출 ===

async def send_to_api(
    session_id: str,
    message: str,
    user_id: str,
    user_name: str,
) -> str:
    """FastAPI 백엔드에 메시지 전송"""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/chat",
                json={
                    "session_id": session_id,
                    "message": message,
                    "user_id": user_id,
                    "user_name": user_name,
                    "platform": "telegram",
                }
            )
            data = response.json()
            return data.get("response", "응답을 생성하지 못했습니다.")
    except Exception as e:
        return f"서버 연결 실패: {str(e)}"

# === 에러 핸들러 ===

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """에러 로깅"""
    print(f"Error: {context.error}")

# === 봇 실행 ===

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # 커맨드 등록
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("reset", reset))

    # 일반 메시지 핸들러
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 에러 핸들러
    app.add_error_handler(error_handler)

    # 폴링 시작
    print("텔레그램 봇 시작...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
```

## 그룹 채팅 지원

```python
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """개인/그룹 채팅 모두 처리"""
    user = update.effective_user
    chat = update.effective_chat
    message = update.message.text

    is_group = chat.type in ("group", "supergroup")

    if is_group:
        # 그룹에서는 봇 멘션 또는 답글일 때만 응답
        bot_username = context.bot.username
        if f"@{bot_username}" not in message and not is_reply_to_bot(update):
            return
        message = message.replace(f"@{bot_username}", "").strip()

    # 그룹에서도 유저별 세션 유지
    session_id = f"tg_{user.id}"

    await update.message.chat.send_action("typing")

    response_text = await send_to_api(
        session_id=session_id,
        message=message,
        user_id=f"telegram_{user.id}",
        user_name=user.first_name,
    )

    await update.message.reply_text(response_text)


def is_reply_to_bot(update: Update) -> bool:
    """봇에게 답글한 메시지인지 확인"""
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user.is_bot
    return False
```

## 인라인 키보드 (버튼)

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("상담 모드 🩺", callback_data="mode_counselor"),
            InlineKeyboardButton("교육 모드 📚", callback_data="mode_teacher"),
        ],
        [
            InlineKeyboardButton("친구 모드 🤝", callback_data="mode_friend"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "안녕하세요! 어떤 모드로 대화할까요?",
        reply_markup=reply_markup,
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """인라인 버튼 콜백"""
    query = update.callback_query
    await query.answer()

    mode = query.data.replace("mode_", "")
    await query.edit_message_text(f"'{mode}' 모드로 시작합니다!")

# 핸들러 등록
app.add_handler(CallbackQueryHandler(button_callback))
```

## 배포 (systemd 서비스)

```bash
# /etc/systemd/system/telegram-bot.service
[Unit]
Description=Telegram Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/project
ExecStart=/home/ubuntu/project/venv/bin/python telegram_bot.py
Restart=always
RestartSec=10
Environment=TELEGRAM_BOT_TOKEN=YOUR_TOKEN
Environment=API_BASE_URL=http://localhost:8000

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

## 주의사항

- 텔레그램 메시지 최대 길이: **4096자** (초과 시 자르기)
- 봇 토큰은 **절대 공개 금지** (.env에 저장)
- `run_polling()`: 개발용 (간단), `run_webhook()`: 프로덕션 (Nginx + SSL 필요)
- 그룹 채팅에서는 **BotFather에서 Privacy Mode OFF** 해야 모든 메시지 수신
- 타이핑 표시(`send_action("typing")`)는 UX에 큰 효과
- 타임아웃 넉넉히 설정 (LLM 응답 120초)
- `python-telegram-bot` 20.x와 21.x는 API가 다름 (21.x 권장)

## 사용 예시

```python
# 최소 봇 (echo)
from telegram.ext import Application, MessageHandler, filters

async def echo(update, context):
    await update.message.reply_text(update.message.text)

app = Application.builder().token("YOUR_TOKEN").build()
app.add_handler(MessageHandler(filters.TEXT, echo))
app.run_polling()
```
