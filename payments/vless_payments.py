from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from keyboards.menu_keyboard import tariff_keyboard, main_keyboard
from keyboards.payment_keyboard import get_payment_methods_keyboard, get_confirm_payment_keyboard
from data_storage import pending_users, waiting_for_payment, tariff_selection
from tg_admin import ADMIN_IDS
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from vless.vless_service import add_client

vless_payment_router = Router()

INBOUND_ID = 1
FLOW = "xtls-rprx-vision"

TARIFFS_VLESS = {
    "month": 199,
    "three_month": 549,
    "six_month": 1299,
    "year": 2799
}


def get_admin_confirmation_keyboard(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_{user_id}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}")]
    ])


@vless_payment_router.callback_query(F.data == "confirm_payment")
async def confirm_payment(call: CallbackQuery):
    pending_users.add(call.from_user.id)
    await call.message.answer("⌛ Заявка на оплату отправлена. Ожидайте подтверждения от администратора.")


@vless_payment_router.callback_query(F.data.startswith("confirm_"))
async def confirm_user_payment(call: CallbackQuery):
    try:
        user_id = int(call.data.split("_")[1])
    except (IndexError, ValueError):
        await call.message.answer("❌ Ошибка: некорректный формат callback_data.")
        return

    if user_id not in pending_users:
        await call.message.answer("❌ Пользователь не ожидает подтверждения.")
        return

    tariff = tariff_selection.get(user_id, "month")

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
            user_name=None  # если хочешь — можешь сохранить username пользователя отдельно
        )

        # Отправляем ключ пользователю
        await call.bot.send_message(
            user_id,
            f"✅ Ваш VLESS ключ:\n\n<code>{key.access_url}</code>\n"
            f"📅 Срок: до {key.expires_at.strftime('%Y-%m-%d')}",
            reply_markup=await tariff_keyboard()
        )

        # Обновляем сообщение у админа
        await call.message.answer(f"✅ Оплата от пользователя {user_id} подтверждена. Ключ выдан.",
                                  reply_markup=await main_keyboard())
    except Exception as e:
        await call.message.answer(f"❌ Ошибка при выдаче ключа: {str(e)}", reply_markup=await tariff_keyboard())

    # Чистим временные данные
    pending_users.remove(user_id)
    waiting_for_payment.pop(user_id, None)
    tariff_selection.pop(user_id, None)


@vless_payment_router.callback_query(F.data.startswith("reject_"))
async def reject_user_payment(call: CallbackQuery):
    user_id = int(call.data.split("_")[1])

    if user_id not in pending_users:
        await call.message.answer("❌ Пользователь не ожидает подтверждения.")
        return

    try:
        # Уведомление пользователю
        await call.message.bot.send_message(
            user_id,
            "❌ Ваша оплата была отклонена администратором. Пожалуйста, свяжитесь с поддержкой или попробуйте ещё раз."
        )

        # Обновление сообщения у админа
        await call.message.edit_caption(
            f"❌ Оплата от пользователя {user_id} была отклонена."
        )

    except Exception as e:
        await call.message.answer(f"Ошибка при отклонении: {str(e)}")

    # Очистка состояний
    pending_users.remove(user_id)
    waiting_for_payment.pop(user_id, None)
    tariff_selection.pop(user_id, None)


TARIFF_NAMES = {
    "month": "<b>199₽/(1 месяц)</b>",
    "three_month": "<b>549₽/(3 месяца)</b>",
    "six_month": "<b>1299₽/(6 месяцев)</b>",
    "year": "<b>2799₽/(1 год)</b>"
}


@vless_payment_router.callback_query(F.data.in_(TARIFFS_VLESS.keys()))
async def handle_tariff_selection(call: CallbackQuery):
    tariff_code = call.data
    tariff_selection[call.from_user.id] = tariff_code

    name = TARIFF_NAMES.get(tariff_code, "неизвестный тариф")

    await call.message.edit_text(
        f"💳 Для оплаты тарифа *{name}* выберите способ ниже:",
        reply_markup=await get_payment_methods_keyboard(back_callback="traffic")
    )


@vless_payment_router.callback_query(F.data == "pay_card")
async def pay_card(call: CallbackQuery):
    tariff = tariff_selection.get(call.from_user.id, "month")
    price = TARIFFS_VLESS.get(tariff, 349)
    await call.message.answer(
        f"💳 Переведите <b>{price}₽</b> на карту и пришлите скриншот платежа:\n\n<b>2200 7001 4268 8075</b>\n"
        "После перевода нажмите «<b>Я оплатил»</b>", reply_markup=await get_confirm_payment_keyboard()
    )


@vless_payment_router.callback_query(F.data == "pay_sbp")
async def pay_sbp(call: CallbackQuery):
    tariff = tariff_selection.get(call.from_user.id, "month")
    price = TARIFFS_VLESS.get(tariff, 349)
    await call.message.answer(
        f"📲 Переведите <b>{price}₽</b> по СБП пришлите скриншот платежа:\n\n<b>+79966163393</b>\n"
        "После перевода нажмите <b>«Я оплатил»</b>", reply_markup=await get_confirm_payment_keyboard()
    )


@vless_payment_router.message(F.photo)
async def handle_screenshot(message: Message):
    user_id = message.from_user.id
    # print(f"[DEBUG] reply_markup: {get_admin_confirmation_keyboard_vless(user_id).inline_keyboard}")
    # print(f"[DEBUG] Отправка админам: confirm_{user_id}")
    file_id = message.photo[-1].file_id

    pending_users.add(user_id)
    waiting_for_payment[user_id] = file_id

    await message.answer("✅ Скриншот принят. Ожидайте подтверждения от администратора.")

    for admin_id in ADMIN_IDS:
        await message.bot.send_photo(
            admin_id,
            file_id,
            caption=f"📸 Оплата от <b>{message.from_user.full_name}</b> (ID: <code>{user_id}</code>) [VLESS]",
            reply_markup=get_admin_confirmation_keyboard(user_id)
        )
