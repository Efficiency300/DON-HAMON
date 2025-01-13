
from config.config import Config
import aiohttp
from aiohttp import ClientTimeout
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_client_history(lead_id: str) -> str:
    url = f'{Config.URL}/{lead_id}'
    headers = {
        'Authorization': Config.SEND_ID,
        'Content-Type': 'application/json'
    }

    try:
        timeout = ClientTimeout(total=2)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                lead_data = await response.json()

        custom_fields = lead_data.get('custom_fields_values', [])
        if not isinstance(custom_fields, list):
            custom_fields = []


        async def get_field_value(field_name):
            return next(
                (
                    field['values'][0]['value']
                    for field in custom_fields
                    if field.get('field_name') == field_name and field.get('values')
                ),
                None
            )

        # Получаем значения полей
        name_value = await get_field_value('Имя')
        number_value = await get_field_value('Номер')
        product_value = await get_field_value('Товар')
        address_value = await get_field_value('Адрес')
        time_value = await get_field_value('Время Доставки')
        date_value = await get_field_value('Дата Доставки')
        pay_type_value = await get_field_value('Способ Оплаты')
        price_value = await get_field_value('Чек')

        # Formulate result string
        return (
            f'Имя: {name_value or "не указано"}\n'
            f'Номер: {number_value or "не указано"}\n'
            f'Товар: {product_value or "не указано"}\n'
            f'Адрес: {address_value or "не указано"}\n'
            f'Время Доставки: {time_value or "не указано"}\n'
            f'Дата Доставки: {date_value or "не указано"}\n'
            f'Способ Оплаты: {pay_type_value or "не указано"}\n'
            f'Чек: {price_value or "не указано"}\n'
        )

    except aiohttp.ClientResponseError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
        return "Ошибка HTTP при получении данных."
    except Exception as e:
        logger.error(f'Unexpected error occurred: {e}', exc_info=True)
        return "Произошла ошибка при обработке данных."