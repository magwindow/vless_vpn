from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_payment_methods_keyboard(back_callback: str = "traffic"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Оплата по СБП", callback_data="pay_sbp")],
        [InlineKeyboardButton(text="💳 Оплата по карте", callback_data="pay_card")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)]
    ])


async def get_confirm_payment_keyboard(back_callback: str = "traffic"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="confirm_payment")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)]
    ])
