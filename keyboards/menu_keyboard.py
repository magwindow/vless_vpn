from aiogram.utils.keyboard import InlineKeyboardBuilder


async def main_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Получить ключ', callback_data='trial')
    keyboard_builder.button(text='Тарифы', callback_data='traffic')
    keyboard_builder.button(text='Мои ключи', callback_data='my_keys')

    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()


async def tariff_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🇷🇺 349₽/мес", callback_data="month")
    kb.button(text="🌍 999₽/3 мес", callback_data="three_month")
    kb.button(text="🧿 1999₽/6 мес", callback_data="six_month")
    kb.button(text="♾️ 3399₽/год", callback_data="year")
    kb.button(text='➕Пригласить друга', callback_data='invite_friend')
    kb.button(text='🔙 В главное меню', callback_data='back_main')
    kb.adjust(2, 2)
    return kb.as_markup()
