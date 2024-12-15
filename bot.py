import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, callback_data

from helpers import validate_age
from keyboards import create_form_keyboard, gender_keyboard

import os
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

user_data = {}


@router.message(Command("start"))
async def start_command_handler(message: Message):
    await message.answer("Здесь ты можешь найти себе компанию на новый год!", reply_markup=create_form_keyboard)


@router.callback_query(F.data == "create_form")
async def create_form_handler(callback: CallbackQuery):
    await callback.message.edit_text("Какого ты пола?", reply_markup=gender_keyboard)
    await callback.answer()


@router.callback_query(F.data.in_({"gender_male", "gender_female"}))
async def gender_selection_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data[user_id] = {"gender": "Мужской" if callback_data == "gender_male" else "Женский"}

    await callback.message.edit_text("Как тебя зовут?")
    await callback.answer()


@router.message(F.text)
async def get_name_handler(message: Message):
    user_id = message.from_user.id
    user_data[user_id]["name"] = message.text

    await message.answer("Сколько тебе лет?")


@router.message(F.text)
async def get_age_handler(message: Message):
    user_id = message.from_user.id

    try:
        age = validate_age(message.text)
    except ValueError:
        await message.answer("Введи реальный возраст")
        return

    user_data[user_id]["age"] = age
    await message.answer("До скольки ты можешь потратить на нг?", reply_markup=ReplyKeyboardRemove())


dp.include_router(router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
