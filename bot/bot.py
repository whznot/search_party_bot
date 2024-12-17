import asyncio
import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto, InputMediaVideo
from dotenv import load_dotenv

from db import init_db
from helpers import update_user_profile
from keyboards import create_form_keyboard, gender_keyboard, confirm_keyboard
from states import ProfileForm

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()

init_db()


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
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

    update_user_profile(message.from_user.id, {"budget": int(message.text)})
    await state.set_state(ProfileForm.media)
    await message.answer("загрузи до трех фоток или видео для анкеты :)")


@router.message(ProfileForm.media)
async def handle_media(message: Message, state: FSMContext):
    data = await state.get_data()
    media_files = data.get("media", [])

    if message.photo:
        file_id = message.photo[-1].file_id
        media_files.append(f"photo:{file_id}")
    elif message.video:
        file_id = message.video.file_id
        media_files.append(f"video:{file_id}")
    else:
        await message.answer("Загрузи фото или видео")
        return

    media_files = media_files[:3]
    await state.update_data(media=media_files)

    user_data = await state.get_data()
    profile_text = f"{user_data.get('name')}, {user_data.get('age')}, {user_data.get('city')}\nБюджет: {user_data.get('budget')}"

    media_group = []
    for idx, media in enumerate(media_files):
        media_type, file_id = media.split(":")
        if media_type == "photo":
            media_group.append(InputMediaPhoto(media=file_id, caption=profile_text if idx == 0 else ""))
        elif media_type == "video":
            media_group.append(InputMediaVideo(media=file_id, caption=profile_text if idx == 0 else ""))

    await message.answer_media_group(media=media_group)
    await message.answer("Вот твоя анкета, все верно?", reply_markup=confirm_keyboard)
    await state.set_state(ProfileForm.confirmation)


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
