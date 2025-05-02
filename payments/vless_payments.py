import html
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select
from database.models import async_session, PaymentRecord
from keyboards.payment_keyboard import get_payment_methods_keyboard, get_confirm_payment_keyboard, check_pay
from data_storage import tariff_selection
from payments.heleket_pay import create_heleket_invoice
from payments.yookassa_pay import create_payment, check_payment_and_send_key

vless_payment_router = Router()

TARIFFS_VLESS = {
    "month": 199,
    "three_month": 549,
    "six_month": 1299,
    "year": 2799
}

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


@vless_payment_router.callback_query(F.data == "check_payment")
async def manual_check(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with async_session() as session:
        result = await session.execute(
            select(PaymentRecord).where(
                PaymentRecord.user_id == user_id,
                PaymentRecord.is_paid == False
            ).order_by(PaymentRecord.id.desc()).limit(1)
        )
        payment_record = result.scalar_one_or_none()

    if payment_record:
        await check_payment_and_send_key(payment_record.payment_id, user_id, callback.bot)
        await callback.answer("Проверяю оплату...", show_alert=False)
    else:
        await callback.message.answer("❗️Не найдено неоплаченных платежей.")


@vless_payment_router.callback_query(F.data == "pay_card")
async def pay_card(call: CallbackQuery):
    user_id = call.from_user.id
    tariff_key = tariff_selection.get(user_id, "month")
    amount = TARIFFS_VLESS.get(tariff_key, 199)

    if amount is None:
        await call.message.answer("Ошибка: неизвестный тариф.")
        return

    payment_url = create_payment(amount, call.from_user.id, tariff_key)
    await call.message.answer(
        f"💸 Перейди по ссылке для оплаты:\n{payment_url}",
        reply_markup=await check_pay(),
        disable_web_page_preview=True
    )


@vless_payment_router.callback_query(F.data == "pay_crypto")
async def pay_crypto(call: CallbackQuery):
    user_id = call.from_user.id
    tariff_code = tariff_selection.get(user_id, "month")
    # print(f"[DEBUG] Выбран тариф: {tariff_code} для пользователя {user_id}")
    rub_amount = TARIFFS_VLESS.get(tariff_code, 199)
    # print(f"[DEBUG] Оплата криптой. Тариф: {tariff_code}, RUB: {rub_amount}")

    try:
        invoice_link = await create_heleket_invoice(rub_amount, user_id=user_id, tariff_name=tariff_code)

        await call.message.answer(
            f"💸 Ссылка для оплаты тарифа:\n{invoice_link}\n\n"
            f"❗️ После оплаты нажмите «Я оплатил»",
            reply_markup=await get_confirm_payment_keyboard()
        )
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка при создании счета: <pre>{html.escape(str(e))}</pre>")
