import aiofiles
import json
import openai
from pathlib import Path
from config.config import Config

client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

async def drop_base():
    file_drop_path = Path("file_drop.json")
    file_json_path = Path("file.json")

    # Если file_drop.json не существует, копируем данные из file.json в file_drop.json
    if not file_drop_path.exists():
        data = {}
        if file_json_path.exists():
            async with aiofiles.open(file_json_path, "r", encoding='utf-8') as fp:
                file_content = await fp.read()
                if file_content:
                    data = json.loads(file_content)

        async with aiofiles.open(file_drop_path, "w", encoding='utf-8') as fp:
            await fp.write(json.dumps(data))

    else:
        # Если file_drop.json существует, удаляем файлы из OpenAI и обновляем базу
        async with aiofiles.open(file_drop_path, "r", encoding='utf-8') as fp:
            file_content = await fp.read()
            if file_content:
                data = json.loads(file_content)
                for file_id in data.keys():
                    try:
                        await client.files.delete(file_id=file_id)
                    except Exception as ex:
                        pass


        if file_json_path.exists():
            async with aiofiles.open(file_json_path, "r", encoding='utf-8') as fp:
                file_content = await fp.read()
                if file_content:
                    data = json.loads(file_content)

        async with aiofiles.open(file_drop_path, "w", encoding='utf-8') as fp:
            await fp.write(json.dumps(data))

        async with aiofiles.open(file_json_path, "w", encoding='utf-8') as fp:
            await fp.write(json.dumps({}))




