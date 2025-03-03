import logging
import os
import gspread
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from oauth2client.service_account import ServiceAccountCredentials

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Telegram API Key
TOKEN = os.getenv("TELEGRAM_API_KEY")

# Google Sheets API
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Подключение к Google Sheets
def connect_google_sheets():
    creds = ServiceAccountCredentials.from_json_keyfile_name("google_credentials.json", SCOPE)
    client = gspread.authorize(creds)
    return client.open_by_key(GOOGLE_SHEETS_ID)

# Подключение к Telegram Bot
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Клавиатура главного меню
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("📚 Пройти тест"))
keyboard.add(KeyboardButton("📊 Моя статистика"))
keyboard.add(KeyboardButton("📝 Проверить сочинение"))

# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я Ботаник🤓, твой помощник по ОГЭ/ЕГЭ! Выбери действие:", reply_markup=keyboard)

# Команда 📚 Пройти тест
@dp.message_handler(lambda message: message.text == "📚 Пройти тест")
async def start_test(message: types.Message):
    sheet = connect_google_sheets().worksheet("Тесты")
    questions = sheet.get_all_records()
    if not questions:
        await message.answer("Пока нет доступных тестов.")
        return
    question = questions[0]
    await message.answer(f"{question['Вопрос']}\n1️⃣ {question['Вариант 1']}\n2️⃣ {question['Вариант 2']}\n3️⃣ {question['Вариант 3']}")

# Команда 📊 Моя статистика
@dp.message_handler(lambda message: message.text == "📊 Моя статистика")
async def show_stats(message: types.Message):
    await message.answer("Твоя статистика пока не доступна. Скоро добавим! 🚀")

# Команда 📝 Проверить сочинение
@dp.message_handler(lambda message: message.text == "📝 Проверить сочинение")
async def check_essay(message: types.Message):
    await message.answer("Отправь мне своё сочинение, и я попробую его проверить! ✍")

@dp.message_handler(content_types=types.ContentType.TEXT)
async def process_essay(message: types.Message):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": message.text}]
    )
    reply = response["choices"][0]["message"]["content"]
    await message.answer(f"📋 Разбор твоего сочинения:\n{reply}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
