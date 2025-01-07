import re
from status_crm.update_lead_status import update_lead_status
import requests
from config.config import Config

async def change_status(lead_id: str, response: str) -> None:

    # URL и заголовки запроса
    url = f'{Config.URL}/{lead_id}'
    headers = {
        'Authorization': Config.SEND_ID,
        'Content-Type': 'application/json'
    }
    match = re.search(r'\b\d{8}\b', response)
    new_status_id = int(match.group(0))




    name = re.search(r"Имя:\s*([^|]+)", response).group(1).strip()
    number = re.search(r"Номер:\s*([^|]+)", response).group(1).strip()
    goods = re.search(r"Товар:\s*([^|]+)", response).group(1).strip()
    address = re.search(r"Адрес:\s*([^|]+)", response).group(1).strip()
    delivery_time = re.search(r"Время Доставки:\s*([^|]+)", response).group(1).strip()
    delivery_date = re.search(r"Дата Доставки:\s*([^|]+)", response).group(1).strip()
    pay_type = re.search(r"Способ Оплаты:\s*([^|]+)", response).group(1).strip()
    price = re.search(r"Чек:\s*([^|]+)", response).group(1).strip()

    # Данные для обновления кастомных полей
    data = {
        'custom_fields_values': [
            {
                'field_id': 1000057,  # ID поля "Имя"
                'values': [{'value': name}]  # Новое значение для поля "Имя"
            },
            {
                'field_id': 1000059,  # ID поля "Номер"
                'values': [{'value': number}]
            },
            {
                'field_id': 1000061,  # ID поля "Товар"
                'values': [{'value': goods}]
            },
            {
                'field_id': 1000063,  # ID поля "Адрес"
                'values': [{'value': address}]
            },
            {
                'field_id': 1000065,  # ID поля "Время Доставки"
                'values': [{'value': delivery_time}]
            },
            {
                'field_id': 1000067,  # ID поля "Дата Доставки"
                'values': [{'value': delivery_date}]
            },
            {
                'field_id': 1000069,  # ID поля "Способ Оплаты"
                'values': [{'value': pay_type}]
            },
            {
                'field_id': 1000071,  # ID поля "Чек"
                'values': [{'value': price}]
            }
        ]
    }

    response = requests.patch(url, headers=headers, json=data)
    await update_lead_status(lead_id, new_status_id)
    # Проверка результата
    if response.status_code == 200:
        print('Кастомные поля успешно обновлены.')
    else:
        print(f'Ошибка при обновлении кастомных полей: {response.status_code}')
        print(response.json())  # Вывод подробностей ошибки

