import os
import asyncio
from fastapi import FastAPI
import uvicorn
from aiogram import Bot, Dispatcher, types
from huggingface_hub import AsyncInferenceClient

# Данные
TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# Инициализация
bot = Bot(token=TOKEN)
dp = Dispatcher()
client = AsyncInferenceClient("Qwen/Qwen2.5-72B-Instruct", token=HF_TOKEN)
app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "ok"}

@dp.message()
async def chat_handler(message: types.Message):
    if not message.text: return
    msg = await message.answer("🤖 Секунду...")
    try:
        response_text = ""
        # Исправленный вызов (сначала await, потом async for)
        stream = await client.chat_completion(
            messages=[
                {"role": "system", "content": "Ты — крутой ИИ-кодер. Отвечай на русском."},
                {"role": "user", "content": message.text}
            ],
            max_tokens=1000, stream=True
        )
        async for token in stream:
            response_text += token.choices[0].delta.content or ""
        
        await msg.edit_text(response_text if response_text.strip() else "Пустой ответ.")
    except Exception as e:
        await msg.edit_text(f"Ошибка: {e}")

async def run_bot():
    print("Запуск бота...")
    await dp.start_polling(bot)

@app.on_event("startup")
async def startup_event():
    # Запускаем бота как фоновую задачу, чтобы не блокировать порт
    asyncio.create_task(run_bot())

if __name__ == "__main__":
    # Запускаем сервер ПЕРВЫМ. Порт 10000 — стандарт для Render
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
