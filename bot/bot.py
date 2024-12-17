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
    user_id = message.from_user.id
    update_user_profile(user_id, {"user_id": user_id})

    await state.set_state(ProfileForm.city)
    await message.answer("В каком городе или области ты готов провести нг?")


@router.message(ProfileForm.city)
async def handle_city(message: Message, state: FSMContext):
    update_user_profile(message.from_user.id, {"city": message.text})
    await state.set_state(ProfileForm.name)
    await message.answer("Как тебя зовут?")


@router.message(ProfileForm.name)
async def handle_name(message: Message, state: FSMContext):
    update_user_profile(message.from_user.id, {"name": message.text})
    await state.set_state(ProfileForm.gender)
    await message.answer("Выбери свой пол:", reply_markup=gender_keyboard)


@router.message(ProfileForm.gender, F.text.in_(["Мужской", "Женский"]))
async def handle_gender(message: Message, state: FSMContext):
    gender = message.text
    update_user_profile(message.from_user.id, {"gender": gender})
    await state.set_state(ProfileForm.age)
    await message.answer("Сколько тебе лет?")


@router.message(ProfileForm.age)
async def handle_age(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (1 < int(message.text) < 100):
        await message.answer("Введи свой настоящий возраст")
        return

    update_user_profile(message.from_user.id, {"age": int(message.text)})
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
    user_id = message.from_user.id

    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    else:
        await message.answer("Загрузи фото или видео")
        return

    uploaded_count = update_user_profile(user_id, updates={}, media_file=file_id, media_type=file_type)
    if uploaded_count > 3:
        await message.answer("Ты уже загрузил максимум 3 медиафайла. Анкета готова.")
        return

    from db import SessionLocal, Profile
    with SessionLocal() as session:
        profile = session.query(Profile).filter_by(user_id=user_id).first()

        profile_text = f"{profile.name}, {profile.age}, {profile.city}\nБюджет: {profile.budget}"

        media_group = []
        if profile.media:
            media_files = profile.media.split(",")
            for idx, media in enumerate(media_files):
                media_type, file_id = media.split(":")
                if media_type == "photo":
                    media_group.append(
                        InputMediaPhoto(media=file_id, caption=profile_text if idx == 0 else "")
                    )
                elif media_type == "video":
                    media_group.append(
                        InputMediaVideo(media=file_id, caption=profile_text if idx == 0 else "")
                    )

        if media_group:
            await message.answer_media_group(media=media_group)
        else:
            await message.answer("Медиа не найдены, заполни анкету заново")

        await message.answer("Вот твоя анкета, все верно?", reply_markup=confirm_keyboard)

        await state.clear()


dp.include_router(router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
