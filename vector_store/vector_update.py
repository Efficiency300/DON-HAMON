

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
        response = await asyncio.to_thread(client.files.create, file=(name + ".txt", file_content),
                                           purpose="assistants")
        return response.id


# Замена использования 'path()' на правильное использование 'os.path.splitext'
async def write_json(file_path: str, data: str) -> None:
    max_retries = 5
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            if not data:
                ic(f"{file_path} - пустой")
                return  # Завершаем выполнение функции, если данные пусты

            # Записываем данные в файл в формате JSON
            async with aiofiles.open(file_path, mode='w', encoding='utf-8') as txt_file:
                await txt_file.write(data)

            # Добавляем файл в OpenAI через API
            file_id = await add_file_to_openai(file_path, os.path.splitext(file_path)[0])

            # Создаем задачу для векторного хранилища OpenAI
            vector_store_task = asyncio.create_task(
                asyncio.to_thread(client.beta.vector_stores.files.create_and_poll,
                                  vector_store_id="vs_j4fGdmZzDMWR5yqyPuoK9aeQ", file_id=file_id)
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


# Функция для получения данных продуктов из Google Sheets
async def fetch_product_records():
    try:
        wks = gc.open('DonHamon').sheet1
        # Получение всех записей
        records = await asyncio.to_thread(wks.get_all_records)

        # Обработка записей
        products_list = format_product_data_as_text(records)
        print(products_list)
        await write_json("product_list.txt", products_list)
        return products_list

    except GSpreadException as e:
        ic(f"Ошибка при получении записей: {e}")
        return []


# Функция для форматирования данных в текстовый формат
def format_product_data_as_text(products_list):
    formatted_text = ""
    for product in products_list:
        formatted_text += (
            f"'img_id': img_{product['ID фото']} ,\n"
            f"'Единица измерения': {product['ед.им']},\n"
            f"'Категория': {product['Категория']},\n"
            f"'Количество кг': {product['количество кг']},\n"
            f"'Примечания': {product['Примечания']},\n"
            f"'Продукт': {product['Продукт']},\n"
            f"'Цена': {product['Цена']},\n"
            f"'наличие свинины': {product['без свинины']},\n\n"
        )
    return formatted_text


if __name__ == "__main__":
    asyncio.run(fetch_product_records())