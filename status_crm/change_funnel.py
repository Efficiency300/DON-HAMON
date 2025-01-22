import aiohttp
from config.config import Config

async def change_funnel(lead_id: str, new_pipeline_id: int, new_status_id: int) -> None:
    url = f"https://infowelloiluz.amocrm.ru/api/v4/leads/{lead_id}"
    headers = {
        "Authorization": f"Bearer {Config.SEND_ID}",
        "Content-Type": "application/json",
    }
    data = {
        "pipeline_id": new_pipeline_id,
        "status_id": new_status_id,
    }

    async with aiohttp.ClientSession() as session:
        async with session.patch(url, headers=headers, json=data) as response:
            if response.status == 200:
                print(await response.json())
            else:
                print(f"Error: {response.status}, {await response.text()}")





