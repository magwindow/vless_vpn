import time
import httpx
import os
import json
import base64
import hashlib
from dotenv import load_dotenv

load_dotenv()

HELEKET_API_KEY = os.getenv("HELEKET_API_KEY")
HELEKET_MERCHANT_ID = os.getenv("HELEKET_MERCHANT_ID")
HELEKET_API_URL = os.getenv("HELEKET_API_URL")


def generate_signature(data: dict) -> str:
    """Создает подпись для Heleket API"""
    json_data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    encoded = base64.b64encode(json_data.encode()).decode()
    signature = hashlib.md5((encoded + HELEKET_API_KEY).encode()).hexdigest()
    return signature


async def create_heleket_invoice(rub_amount: int, user_id: int, tariff_name: str) -> str:
    """
    Создает инвойс на оплату через Heleket.
    Возвращает URL на оплату.
    """
    data = {
        "amount": str(rub_amount),
        "currency": "RUB",
        "to_currency": "USDT",
        "order_id": f"{user_id}_{int(time.time())}",
        "description": f"Тариф {tariff_name} для пользователя {user_id}",
    }

    headers = {
        "merchant": HELEKET_MERCHANT_ID,
        "sign": generate_signature(data),
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{HELEKET_API_URL}", headers=headers, json=data)

    if response.status_code == 200:
        invoice_data = response.json()
        url = invoice_data["result"]["url"]
        # print(invoice_data)
        return url
    else:
        raise Exception(f"Ошибка при создании инвойса: {response.status_code} - {response.text}")


