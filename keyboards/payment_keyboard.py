from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def get_payment_methods_keyboard(back_callback: str = "traffic"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплата по карте", callback_data="pay_card")],
        [InlineKeyboardButton(text="💰 Оплата криптовалютой", callback_data="pay_crypto")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)]
    ])


async def get_confirm_payment_keyboard(back_callback: str = "traffic"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="confirm_payment")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)]
    ])


async def check_pay():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Проверить оплату", callback_data="check_payment")
    kb.button(text='Назад', callback_data='back_main')
    return kb.as_markup()