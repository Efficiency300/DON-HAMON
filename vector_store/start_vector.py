from vectore_test import fetch_product_records
from vector_drop import drop_base
import schedule
import time
import asyncio

# Wrapper function to ensure drop_base is only called if fetch_product_records succeeds
async def run_tasks():
    try:
        # Выполнение fetch_product_records
        await fetch_product_records()
        print("fetch_product_records выполнен успешно.")

        # Выполнение drop_base только если fetch_product_records прошел успешно
        await drop_base()
        print("drop_base выполнен успешно.")
    except Exception as e:
        print(f"Ошибка при выполнении fetch_product_records: {e}")
        print("drop_base не будет выполнен.")

# Helper function to run asyncio tasks
def run_asyncio_task(task):
    asyncio.run(task)

# Schedule both tasks to run at 9:28 AM
schedule.every().day.at("18:59").do(run_asyncio_task, run_tasks())

# Schedule both tasks to run at 6:00 PM
schedule.every().day.at("18:00").do(run_asyncio_task, run_tasks())

# Infinite loop to keep running scheduled tasks
while True:
    schedule.run_pending()
    time.sleep(1)