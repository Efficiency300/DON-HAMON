import re
import aiohttp
import logging
import requests
from icecream import ic
from config.config import Config
from pathlib import Path


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent
PHOTOS_DIR = BASE_DIR / "photos"

async def send_message(amojo_id, chat_token, message, chat_id , photo_id):
    """
    Отправляет сообщение с возможными фотографиями.
    """
    try:

        message = re.sub(r'~|【.*?】.*', '', message)

        # Разбиваем сообщение на части
        parts = re.split(r"\n\s*\n", message)

        ic(parts , photo_id)

        for photo in photo_id:
            photo_paths = PHOTOS_DIR / photo["photo_id"]

            data = {
            "message": photo["name"],
            "chat_id": chat_id,
            "chat_token": chat_token,
            "amojo_id": amojo_id,
            "token": Config.SEND_ID
            }

        # Формируем файлы для отправки
            files = {}

            if photo_paths.exists():
                files["file"] = (photo_paths.name, open(photo_paths, "rb"), "image/png")
            else:
                ic(f"Файл {photo_paths} не найден.")

        # Отправка запроса
            response = requests.post(Config.MESSAGE_SAND_URL, data=data, files=files if files else None)
            response.raise_for_status()
            ic("Сообщение успешно отправлено:", response.json())

        # Закрываем открытые файлы
            for file in files.values():
                file[1].close()



        for part in parts:
            # Проверяем наличие фотографий

            data = {
                "message": part.strip(),
                "chat_id": chat_id,
                "chat_token": chat_token,
                "amojo_id": amojo_id,
                "token": Config.SEND_ID
            }


            # Отправка запроса
            async with aiohttp.ClientSession() as session:
                async with session.post(Config.MESSAGE_SAND_URL, data=data) as response:
                    if response.status == 200:
                        logger.info("Сообщение успешно отправлено")
                    else:
                        response.raise_for_status()


    except Exception as e:
        ic(f"Произошла ошибка: {e}")