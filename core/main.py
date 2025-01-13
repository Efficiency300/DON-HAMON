import asyncio
import json
from collections import defaultdict
from utils.message_to_group import send_message_to_group
from status_crm.forward_deal_message import chat_history_sort
from status_crm.amo_client_history import get_client_history
from services.MarkdownProcessor import MarkdownProcessor
from status_crm.amo_status_change import change_status
from services.photo_service import PhotoService
from services.stt_service import STTService
from utils.get_converse import get_converse
from amo.send_message import send_message
from services.llm_service import thread
from utils.logger import setup_logger
from amo.amo_data import amo_api_data

logger = setup_logger()

message_buffers = defaultdict(list)
message_timers = {}
BUFFER_DELAY = 5
def is_image(url: str) -> bool:
    return isinstance(url, str) and url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
def is_voice(url: str) -> bool:
    return isinstance(url, str) and url.lower().endswith(('.m4a', '.mp3', '.wav', '.ogg'))

async def process_attachments(user_input_list: list,photo_service: PhotoService,stt_service: STTService) -> tuple[str, str, str]:
    """Обрабатывает вложения и формирует текстовые данные."""
    image_description = ""
    transcribed_text = ""
    processed_text_parts = []

    for msg in user_input_list:
        if isinstance(msg, dict):
            if msg.get("type") == "image":
                image_url = msg.get("content")
                image_response = await photo_service.process_image_from_url(image_url)
                if image_response:
                    image_data = json.loads(image_response)
                    image_description += f"\n\nКонтекст изображения: {image_data.get('description', '')}"
            elif msg.get("type") == "voice":
                voice_url = msg.get("content")
                transcribed = stt_service.transcribe(voice_url)
                if transcribed:
                    transcribed_text += f"\n\nТранскрибированное голосовое сообщение: {transcribed}"
        else:
            processed_text_parts.append(msg)

    return "\n".join(processed_text_parts), image_description, transcribed_text


async def send_responses(clean_text: str, amo_data: dict, chat_id: str , photo_id) -> None:
            await send_message(
                amo_data["amojo_id"],
                amo_data["chat_token"],
                clean_text,
                chat_id,
                photo_id

            )


async def process_messages(chat_id: str, entity_id: str) -> None:
    """Обрабатывает сообщения из буфера."""
    try:
        user_input_list = message_buffers.pop(chat_id, [])
        photo_service = PhotoService()
        stt_service = STTService()

        # Обработка вложений
        processed_text, image_description, transcribed_text = await process_attachments(
            user_input_list, photo_service, stt_service
        )

        # Формируем итоговый ввод
        user_input = f"{processed_text}{image_description}{transcribed_text}"
        logger.info(f"Итоговый ввод для LLM: {user_input}")

        # Получаем данные из AmoCRM
        amo_data = await amo_api_data()
        amo_history = await get_client_history(entity_id)
        logger.info(f"История клиента: {amo_history}")

        # Отправка в LLM
        user_input = f"ответ клиента: {user_input}"
        ai_answer, list_ai , photo_id= await thread(user_input, chat_id)
        clean_text = await MarkdownProcessor.strip_markdown(ai_answer)
        print(photo_id)
        logger.info(f"Ответ LLM: {clean_text}")

        # Отправка ответа
        await send_responses(clean_text, amo_data, chat_id , photo_id)

        # Обновление CRM
        converse = await get_converse(list_ai)
        crm_data = await chat_history_sort(converse, amo_history)
        logger.info(f"CRM данные для обновления: {crm_data}")
        await send_message_to_group(crm_data)
        await change_status(entity_id, crm_data)


    except Exception as e:
        logger.error(f"Произошла ошибка при обработке: {e}", exc_info=True)


async def handle_incoming_message(message_text: str, chat_id: str, result: str, entity_id: str) -> None:
    """Обрабатывает входящее сообщение."""
    if message_text:
        message_buffers[chat_id].append(message_text)

    if result:
        if is_image(result):
            message_buffers[chat_id].append({"type": "image", "content": result})
        elif is_voice(result):
            message_buffers[chat_id].append({"type": "voice", "content": result})

    if chat_id in message_timers:
        message_timers[chat_id].cancel()

    message_timers[chat_id] = asyncio.create_task(timer_task(chat_id, entity_id))


async def timer_task(chat_id: str, entity_id: str) -> None:
    await asyncio.sleep(BUFFER_DELAY)
    await process_messages(chat_id, entity_id)


async def main(message_text: str, chat_id: str, result: str, entity_id: str) -> None:
    await handle_incoming_message(message_text, chat_id, result, entity_id)
