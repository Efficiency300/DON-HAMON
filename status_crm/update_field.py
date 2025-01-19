import re
import aiohttp
from config.config import Config
from status_crm.change_stage import change_stage

async def update_field(lead_id: str, response_text: str) -> None:
    url = f"{Config.URL}/{lead_id}"
    headers = {
        'Authorization': Config.SEND_ID,
        'Content-Type': 'application/json'
    }

    try:

        name = re.search(r"Имя:\s*([^|]+)", response_text)
        number = re.search(r"Номер:\s*([^|]+)", response_text)
        goods = re.search(r"Товар:\s*([^|]+)", response_text)
        address = re.search(r"Адрес:\s*([^|]+)", response_text)
        delivery_time = re.search(r"Время Доставки:\s*([^|]+)", response_text)
        delivery_date = re.search(r"Дата Доставки:\s*([^|]+)", response_text)
        pay_type = re.search(r"Способ Оплаты:\s*([^|]+)", response_text)
        price = re.search(r"Чек:\s*([^|]+)", response_text)
        match_status = re.search(r'\b\d{8}\b', response_text)

        if not all([name, number, goods, address, delivery_time, delivery_date, pay_type, price,match_status]):
            raise ValueError("Missing required data in response text.")


        name = name.group(1).strip()
        number = number.group(1).strip()
        goods = goods.group(1).strip()
        address = address.group(1).strip()
        delivery_time = delivery_time.group(1).strip()
        delivery_date = delivery_date.group(1).strip()
        pay_type = pay_type.group(1).strip()
        price = price.group(1).strip()
        new_status_id = int(match_status.group(0))


        data = {
            'custom_fields_values': [
                {'field_id': 1000057, 'values': [{'value': name}]},
                {'field_id': 1000059, 'values': [{'value': number}]},
                {'field_id': 1000061, 'values': [{'value': goods}]},
                {'field_id': 1000063, 'values': [{'value': address}]},
                {'field_id': 1000065, 'values': [{'value': delivery_time}]},
                {'field_id': 1000067, 'values': [{'value': delivery_date}]},
                {'field_id': 1000069, 'values': [{'value': pay_type}]},
                {'field_id': 1000071, 'values': [{'value': price}]}
            ]
        }


        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as response:
                if response.status == 200:
                    print("Custom fields successfully updated.")
                else:
                    print(f"Error updating custom fields: {response.status}")
                    print(await response.json())

        await change_stage(lead_id, new_status_id)
    except Exception as e:
        print(f"Error in change_status: {e}")