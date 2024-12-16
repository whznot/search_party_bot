from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

create_form_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать анкету")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

gender_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
