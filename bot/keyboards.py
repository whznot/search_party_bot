from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

create_form_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Создать анкету", callback_data="create_form")]
    ]
)

gender_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Мужской", callback_data="gender_male")],
        [InlineKeyboardButton(text="Женский", callback_data="gender_female")]
    ]
)
