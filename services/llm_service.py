import json
from asyncio import Lock
from icecream import ic
from openai import AsyncOpenAI
from config.config import Config
from pathlib import Path
from services.promt import promt
from handlers.JsonDataBase import JSONDatabase

BASE_DIR = Path(__file__).resolve().parent.parent
talk_id_json = f"{BASE_DIR}/config/thread_id.json"
file_lock = Lock()
db = JSONDatabase(talk_id_json)



tools = [
    {
        "type": "file_search",
        "file_search": {
            "max_num_results": 10,  # Example configuration
            "ranking_options": {
                "score_threshold": 0.1  # Example threshold
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Возвращает текущее время.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "send_photo_and_description",
            "description": "Отправляет фото товара из базы по его уникальному номеру",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_number": {
                        "type": "string",
                        "description": "ID фото"
                    },
                    "name": {
                        "type": "string",
                        "description": "название продукта"
                    }
                },
                "required": ["item_number" , "name"]
            }
        }
    },
]

async def thread(message_text: str, chat_id: str) -> tuple[str, dict | None, list | None]:
    try:
        async with file_lock:
            client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY, default_headers={"OpenAI-Beta": "assistants=v2"})

            # Retrieve or create a thread ID for the chat
            thread_id = await db.get(chat_id) if await db.exists(chat_id) else None
            if not thread_id:
                thread = await client.beta.threads.create()
                thread_id = thread.id
                await db.add(chat_id, thread_id)

            # Send message to the thread
            await client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message_text
            )

            # Initialize photo_id to avoid unbound variable
            photo_id = []

            # Run the model and poll results
            run = await client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                model="gpt-4o",
                assistant_id=Config.ASSIST_ID,
                temperature=0.2,
                instructions=promt,
                tools=tools
            )

            if run.status == 'requires_action':
                tool_outputs = []

                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    try:

                        tool_args = json.loads(tool_call.function.arguments)

                        if "item_number" in tool_args and "name" in tool_args:
                            numbers = tool_args['item_number']
                            name_of_product = tool_args['name']
                            photo_id.append({"name": name_of_product, "photo_id": f"{numbers}.jpg"})
                            result = "photo_send_sucsesfuly"
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps(result)
                            })
                        else:
                            ic(f"Недостаточно данных в tool_args: {tool_args}")

                    except Exception as tool_error:
                        ic(f"Ошибка обработки инструмента {tool_call.id}: {tool_error}")

                # Submit tool outputs and poll for results
                run = await client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

            if run.status == "completed":
                # Получаем сообщения из потока
                messages = await client.beta.threads.messages.list(thread_id=thread_id)
                messages_json = json.loads(messages.model_dump_json())

                try:
                    response = messages_json["data"][0]["content"][0]["text"]["value"]
                except (IndexError, KeyError) as parse_error:
                    ic(f"Ошибка разбора ответа: {parse_error}")
                    response = "Error parsing response"

                return response, messages_json, photo_id

            else:
                ic(f"Запуск завершился со статусом: {run.status}")
                return "Model run not completed", None, None

    except Exception as e:
        ic(f"Общая ошибка: {e}")
        return str(e), None, None
