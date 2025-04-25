from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.models import async_session, VlessKey
from keyboards.menu_keyboard import tariff_keyboard, main_keyboard
from vless.vless_service import add_client
from sqlalchemy import select

vless_router = Router()

INBOUND_ID = 1
FLOW = "xtls-rprx-vision"


# === Триал на 3 дня ===
@vless_router.callback_query(F.data == "trial")
async def send_trial(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with async_session() as session:
        existing = await session.execute(select(VlessKey).where(VlessKey.chat_id == user_id))
        if existing.scalars().first():
            await callback.message.answer("❗️У вас уже есть активный VLESS ключ.", reply_markup=await main_keyboard())
            return

    try:
        key = await add_client(
            inbound_id=INBOUND_ID,
            total_gb=5,
            expiry_days=3,
            flow=FLOW,
            chat_id=user_id,
            user_name=callback.from_user.username
        )

        await callback.message.answer(
            f"✅ Ваш пробный VLESS ключ на 3 дня:\n\n<code>{key.access_url}</code>\n"
            f"⏳ Действителен до: {key.expires_at.strftime('%Y-%m-%d')}", reply_markup=await main_keyboard()
        )
    except Exception as e:
        await callback.message.answer(f"Ошибка: {str(e)}")


# === Обработка платных тарифов ===
@vless_router.callback_query(F.data.in_(["month", "three_month", "six_month", "year"]))
async def send_paid(callback: CallbackQuery):
    user_id = callback.from_user.id
    tariff = callback.data

    tariffs = {
        "month": {"gb": 100, "days": 30},
        "three_month": {"gb": 300, "days": 90},
        "six_month": {"gb": 600, "days": 180},
        "year": {"gb": 9999, "days": 365},
    }

    try:
        t = tariffs[tariff]
        key = await add_client(
            inbound_id=INBOUND_ID,
            total_gb=t["gb"],
            expiry_days=t["days"],
            flow=FLOW,
            chat_id=user_id,
            user_name=callback.from_user.username
        )

        await callback.message.answer(
            f"✅ Ваш VLESS ключ:\n\n<code>{key.access_url}</code>\n"
            f"📅 Срок: до {key.expires_at.strftime('%Y-%m-%d')}", reply_markup=await tariff_keyboard()
        )
    except Exception as e:
        await callback.message.answer(f"Ошибка: {str(e)}")


@vless_router.callback_query(F.data == "traffic")
async def show_tariffs(callback: CallbackQuery):
    keyboard = await tariff_keyboard()
    await callback.message.edit_text(
        "💳 Выберите тариф для подключения VLESS:",
        reply_markup=keyboard
    )


@vless_router.callback_query(F.data == "manual")
async def manual_vless(callback: CallbackQuery):
    await callback.message.edit_text(
        "Вся установка займет не более 2-х минут.\n\n"
        "<b>1. Скачайте приложение:</b>\n\n"
        '📱 <a href="https://apps.apple.com/ru/app/streisand/id6450534064">Скачать на iOS</a>\n'
        '📱 <a href="https://play.google.com/store/apps/details?id=com.v2raytun.android">Скачать на Android</a>\n\n'
        "<b>2. Получите VPN ключ.</b>\n\n"
        'Получите ключ по кнопке "Получить ключ".\n\n'
        "<b> Активируйте VPN ключ.</b>\n\n"
        "Скопируйте полученный ключ и откройте скаченное приложение.\n\n"
        'Нажмите на плюсик в правом верхнем углу экрана и нажмите на кнопку "Вставить из буфера".\n\n'
        "Нажмите на большую кнопку подключения в центре экрана.",
        reply_markup=await main_keyboard()
    )

