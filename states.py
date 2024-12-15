from aiogram.fsm.state import StatesGroup, State


class ProfileForm(StatesGroup):
    city = State()
    name = State()
    gender = State()
    age = State()
    budget = State()
    media = State()
    confirmation = State()
