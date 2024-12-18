import asyncio
import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.media_group import MediaGroupBuilder
from dotenv import load_dotenv

from db import init_db
from keyboards import create_form_keyboard, gender_keyboard, confirm_keyboard, save_media
from states import ProfileForm

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

init_db()


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await state.update_data(media=[])
    await message.answer("Здесь ты можешь найти себе компанию на новый год!", reply_markup=create_form_keyboard)


@router.message(F.text == "Создать анкету")
async def create_form_handler(message: Message, state: FSMContext):
    await state.set_state(ProfileForm.city)
    await message.answer("В каком городе или области ты готов провести нг?")


@router.message(ProfileForm.city)
async def handle_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(ProfileForm.name)
    await message.answer("Как тебя зовут?")


@router.message(ProfileForm.name)
async def handle_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ProfileForm.gender)
    await message.answer("Выбери свой пол:", reply_markup=gender_keyboard)


@router.message(ProfileForm.gender, F.text.in_(["Мужской", "Женский"]))
async def handle_gender(message: Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await state.set_state(ProfileForm.age)
    await message.answer("Сколько тебе лет?")


@router.message(ProfileForm.age)
async def handle_age(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (6 <= int(message.text) <= 99):
        await message.answer("Введи свой настоящий возраст")
        return

    await state.update_data(age=int(message.text))
    await state.set_state(ProfileForm.budget)
    await message.answer("До скольки ты готов потратить на нг?")


@router.message(ProfileForm.budget)
async def handle_budget(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введи сумму числом")
        return

    await state.update_data(budget=int(message.text))
    await state.set_state(ProfileForm.media)
    await message.answer("загрузи до трех фоток или видео для анкеты :)")


async def show_profile(message:Message, state:FSMContext):
    await message.answer("Вот так выглядит твоя анкета:")
    data = await state.get_data()
    md = MediaGroupBuilder()
    for i in data['media']:
        md.add_photo(i)
    await bot.send_media_group(chat_id=message.chat.id, media=md.build())
    await message.answer("Нрав?", reply_markup=confirm_keyboard)




@router.message(ProfileForm.media)
async def handle_media(message: Message, state: FSMContext):
    data = await state.get_data()

    if len(data["media"]) == 3:
        await show_profile(message, state)
    elif (message.photo or message.video) and len(data["media"]) < 3:
        if message.photo:
            data["media"].append(message.photo[-1].file_id)
            await state.update_data(media=data["media"])
            await message.answer("+ контентик, это всё?", reply_markup=save_media)
        else:
            data["media"].append(message.video.file_id)
            await state.update_data(media=data["media"])

    elif not message.photo or not message.video:
        await message.answer("Отправь фотки или видео")


# @router.message(ProfileForm.media & F.text == "Это все, сохранить как есть")


# @router.message(ProfileForm.send_profile)
# async def send_profile(message: Message, state: FSMContext):


@router.message(ProfileForm.confirmation, F.text == "✅ Подтвердить")
async def confirm_profile(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()

    from db import SessionLocal, Profile
    with SessionLocal() as session:
        profile = Profile(
            user_id=user_id,
            city=user_data.get("city"),
            name=user_data.get("name"),
            gender=user_data.get("gender"),
            age=user_data.get("age"),
            budget=user_data.get("budget"),
            media=",".join(user_data.get("media", []))
        )
        session.add(profile)
        session.commit()

        await state.clear()
        await message.answer("Анкета создана, смотреть ленту?")


dp.include_router(router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
