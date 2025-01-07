from config.config import Config
import aiohttp
import re
from icecream import ic






async def send_message_to_group(response2: str) -> None:
    message_text = response2  # Текст вашего сообщения


    # Извлечение данных с помощью регулярных выражений
    details = {}
    details['Товар'] = re.search(r"Товар:\s*([^|]+)", message_text).group(1).strip()
    details['Имя'] = re.search(r"Имя:\s*([^|]+)", message_text).group(1).strip()
    details['Номер'] = re.search(r"Номер:\s*[^\d]*([\d\s()-]+)", message_text).group(1).strip()
    details['Адрес'] = re.search(r"Адрес:\s*([^|]+)", message_text).group(1).strip()
    details['Способ Оплаты'] = re.search(r"Способ Оплаты:\s*([^|]+)", message_text).group(1).strip()
    details['Чек'] = re.search(r"Чек:\s*([^|]+)", message_text).group(1).strip()
    details['Время Доставки'] = re.search(r"Время Доставки:\s*([^|]+)", message_text).group(1).strip()
    details['Дата Доставки'] = re.search(r"Дата Доставки:\s*([^|]+)", message_text).group(1).strip()




    # Проверка на наличие "Перенести сделку: Yes" в сообщении
    if re.search(r"Перенести\s*сделку:\s*Yes\s*\|", response2):
        # Если найдена приписка, отправляем сообщение с извлеченными данными
        formatted_message = (
            "❗**Новый Заказ**❗\n\n"  # Добавлена пустая строка между заголовком и основным текстом
            f"🍖Заказ: {details['Товар']} \n"
            f"✍️Имя клиента: {details['Имя']} \n"
            f"📱Номер телефона: {details['Номер']} \n"
            f"🏠Адрес доставки: {details['Адрес']} \n"
            f"💳Способ оплаты: {details['Способ Оплаты']} \n"
            f"💵Итоговая сумма оплаты: {details['Чек']} сум \n"
            f"⌛Время доставки: {details['Время Доставки']} \n"
            f"📅дата доставки: {details['Дата Доставки']} \n"

        )


        try:

            url = f'https://api.telegram.org/bot{Config.TG_BOT_TOKEN}/sendMessage'
            payload = {
                'chat_id': Config.ORDER_GROUP_ID,
                'text': formatted_message
            }
            async with aiohttp.ClientSession() as session:
                await session.post(url, data=payload)


            ic("Сообщение успешно отправлено.")
        except Exception as e:
            ic(f"Ошибка отправки сообщения: {e}")
    else:
        ic("Приписка 'Перенести сделку: Yes' не найдена.")
