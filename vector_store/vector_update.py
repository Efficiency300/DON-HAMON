

import aiofiles
import json
import asyncio
import openai
import os
import gspread
from gspread import GSpreadException
from icecream import ic
from config.config import Config
from pathlib import Path
client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

lock = asyncio.Lock()  # Глобальная блокировка


BASE_DIR = Path(__file__).resolve().parent.parent
TALK_ID_JSON_PATH = BASE_DIR / "Service_Account.json"
# Создание клиента для Google Sheets
gc = gspread.service_account(filename=TALK_ID_JSON_PATH)


async def add_file_to_openai(path, name):
    async with aiofiles.open(path, 'rb') as f:
        file_content = await f.read()
        response = await asyncio.to_thread(client.files.create, file=(name + ".txt", file_content), purpose='assistants')
        return response.id


async def write_json(file_path: str, data: dict) -> None:
    max_retries = 5
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            if not data:
                ic(f"{file_path} - пустой")
                return  # Завершаем выполнение функции, если данные пусты

            # Записываем данные в файл в формате JSON
            async with aiofiles.open(file_path, mode='w', encoding='utf-8') as txt_file:
                await txt_file.write(json.dumps(data, ensure_ascii=False, indent=4) + "\n")

            # Добавляем файл в OpenAI через API
            file_id = await add_file_to_openai(file_path, os.path.splitext(file_path)[0])

            # Создаем задачу для векторного хранилища OpenAI
            vector_store_task = asyncio.create_task(
                asyncio.to_thread(client.beta.vector_stores.files.create_and_poll, vector_store_id=Config.VECTOR_ID, file_id=file_id)
            )

            # Работаем с локальным JSON (файлом данных) с блокировкой
            async with lock:
                # Проверяем существование файла перед открытием
                if not os.path.exists("file.json"):
                    # Создаем пустой файл, если он не существует
                    async with aiofiles.open("file.json", mode='w', encoding='utf-8') as fp:
                        await fp.write("{}")

                async with aiofiles.open("file.json", mode='r+', encoding='utf-8') as fp:
                    try:
                        file_content = await fp.read()
                        data_store = json.loads(file_content) if file_content else {}
                    except json.JSONDecodeError:
                        data_store = {}

                    # Добавляем новый файл в локальный JSON
                    if isinstance(data_store, dict):
                        data_store[file_id] = "data"
                    else:
                        raise ValueError("Data store is not a valid dictionary")

                    # Перемещаем указатель на начало файла и перезаписываем его
                    await fp.seek(0)
                    await fp.write(json.dumps(data_store, ensure_ascii=False, indent=4))
                    await fp.truncate()

            # Дожидаемся завершения задачи добавления файла в векторное хранилище
            await vector_store_task

            break  # Успешная операция, выходим из цикла

        except Exception as e:
            ic(f"Ошибка при записи JSON или обновлении данных (попытка {attempt + 1} из {max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                ic("Максимальное количество попыток достигнуто. Операция завершена с ошибкой.")


async def fetch_product_records():
    wks = gc.open('DonHamon').sheet1
    expected_headers = ["Продукт", "Цена", "Категория", "ID фото", "Примечания", "без свинины", "ед.им" ,"количество кг"]

    try:
        # Получение всех записей с использованием expected_headers
        records = await asyncio.to_thread(wks.get_all_records, expected_headers=expected_headers)

    except GSpreadException as e:
        ic(f"Ошибка при получении записей: {e}")
        return []

    # Преобразование данных в нужный формат
    products_list = parse_product_data(records)
    ic(products_list)
    await write_json("product_list.json", products_list)  # Передача списка продуктов в функцию write_json
    return products_list

# Функция для парсинга данных продуктов
def parse_product_data(records):
    products_list = []
    for record in records:
        ic(record)
        product_dict = {
            "Продукт": record.get("Продукт", ""),
            "Цена": record.get("Цена", ""),
            "Категория": record.get("Категория", ""),
            "Примечания": record.get("Примечания", ""),
            "наличение свинины": record.get("без свинины", ""),
            "Количество кг": record.get("количество кг", ""),
            "Единица измерения": record.get("ед.им", ""),
            "ID фото": record.get("ID фото", "")
        }
        products_list.append(product_dict)
    return products_list



asyncio.run(fetch_product_records())