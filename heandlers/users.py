from keyboards.menu_keyboard import main_keyboard
from database.crud import add_user_if_not_exists
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router_users: Router = Router()


@router_users.message(CommandStart())
async def start_command(message: Message):
    await add_user_if_not_exists(message.from_user.id, message.from_user.username)
    await message.answer(text='Привет! Добро пожаловать в бота, который поможет вам выбрать лучший VPN',
                         reply_markup=await main_keyboard())