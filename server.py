import os
import asyncio
import uuid
import json
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher, types
import g4f

# Настройки из твоего старого кода
LOG_FILE = "ai_bot_logs.json"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8599073108:AAGxNlkRuWIrTz5IoDv4EQy53gsEAjlJRTQ")

# Инициализация
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Твой класс Logger
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False)

async def get_ai_response(message):
    try:
        # Бесплатный GPT-4 через g4f вместо локальной Ollama
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": message}],
        )
        return response
    except Exception as e:
        return f"Ошибка ИИ: {e}"

@app.post("/chat")
async def web_chat(request: Request):
    data = await request.json()
    user_message = data.get("text", "")
    answer = await get_ai_response(user_message)
    return {"success": True, "answer": answer}

@dp.message()
async def handle_tg(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")
    answer = await get_ai_response(message.text)
    await message.answer(answer)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(dp.start_polling(bot))

if __name__ == "__main__":
    import uvicorn
    # Порт 7860 обязателен для работы в Spaces
    uvicorn.run(app, host="0.0.0.0", port=7860)