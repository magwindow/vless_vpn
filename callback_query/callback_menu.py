from aiogram import Router, F
from aiogram.types import CallbackQuery

from invite_friends import handle_invite
from keyboards.menu_keyboard import main_keyboard

router_call = Router()


@router_call.callback_query(F.data == 'invite_friend')
async def invite_friend_callback(call: CallbackQuery):
    await call.answer()  # убирает "часики"
    await handle_invite(call.message)


@router_call.callback_query(F.data == "back_main")
async def back_to_main_menu(call: CallbackQuery):
    await call.message.edit_text(
        "🏠 Главное меню:",
        reply_markup=await main_keyboard()
    )
