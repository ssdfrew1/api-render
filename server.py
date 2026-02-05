import os
import asyncio
import httpx
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from huggingface_hub import AsyncInferenceClient

# --- НАСТРОЙКИ ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
# Сюда вставь свою ссылку от Render после первого деплоя
RENDER_URL = "https://api-render-ssdf.onrender.com/" 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Модель Qwen 2.5 72B — мощная, бесплатная на HF и идеально знает русский
client = AsyncInferenceClient("Qwen/Qwen2.5-72B-Instruct", token=HF_TOKEN)

# --- ФУНКЦИЯ КИП-АЛАЙВ (ЧТОБЫ НЕ СПАЛ) ---
async def keep_alive():
    async with httpx.AsyncClient() as http_client:
        while True:
            try:
                await http_client.get(RENDER_URL)
                print(f"[{datetime.now()}] Self-ping successful")
            except Exception as e:
                print(f"[{datetime.now()}] Self-ping failed: {e}")
            await asyncio.sleep(600)  # Пинг раз в 10 минут

# --- ОБРАБОТКА КОМАНД ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Я жив! Твой личный ИИ на базе Hugging Face готов к работе. Пиши любой вопрос.")

# --- ОБРАБОТКА СООБЩЕНИЙ ---
@dp.message()
async def chat_handler(message: types.Message):
    if not message.text:
        return

    # Отправляем временный статус
    status_msg = await message.answer("🤖 Печатает...")

    try:
        response_text = ""
        # Стриминг ответа от модели
        async for token in client.chat_completion(
            messages=[
                {"role": "system", "content": "Ты — крутой и остроумный ИИ-помощник. Отвечай всегда на русском языке."},
                {"role": "user", "content": message.text}
            ],
            max_tokens=1000,
            stream=True
        ):
            chunk = token.choices[0].delta.content or ""
            response_text += chunk

        # Редактируем сообщение финальным текстом
        if response_text.strip():
            await status_msg.edit_text(response_text)
        else:
            await status_msg.edit_text("Модель прислала пустой ответ. Попробуй еще раз.")

    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка нейронки: {e}")

# --- ЗАПУСК ---
async def main():
    print("Бот запускается...")
    # Запускаем пинг в фоновом режиме
    asyncio.create_task(keep_alive())
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен")
