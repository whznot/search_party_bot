import asyncio
import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

from keyboards import create_form_keyboard

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Здесь ты можешь найти себе компанию на новый год!", reply_markup=create_form_keyboard)


@router.callback_query(F.data == "create_form")
async def


dp.include_router(router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
