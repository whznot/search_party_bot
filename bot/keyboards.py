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

confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Подтвердить"), KeyboardButton(text="🔄 Заполнить анкету заново")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

save_media = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Это все, сохранить как есть")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
