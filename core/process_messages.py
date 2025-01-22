from handlers.message_to_group import send_message_to_group
from status_crm.forward_deal_message import chat_history_sort
from status_crm.client_history import client_history
from handlers.MarkdownProcessor import MarkdownProcessor
from status_crm.update_field import update_field
from handlers.get_converse import get_converse
from server.send_message import send_message
from services.llm_service import thread
from handlers.logger import setup_logger
from server.amo_data import amo_api_data

logger = setup_logger()

async def send_responses(clean_text: str, amo_data: dict, chat_id: str , photo_id) -> None:
            await send_message(amo_data["amojo_id"], amo_data["chat_token"], clean_text, chat_id, photo_id)
async def process_messages(chat_id: str, entity_id: str , processed_text: tuple[str, str , str]) -> None:

    try:
        # Получаем данные из AmoCRM
        amo_data = await amo_api_data()
        amo_history = await client_history(entity_id)

        # Отправка в LLM
        user_input = f"ответ клиента: {processed_text}"
        ai_answer, list_ai , photo_id= await thread(user_input, chat_id)
        clean_text = await MarkdownProcessor.strip_markdown(ai_answer)
        logger.info(f"Ответ LLM: {clean_text}")

        # Отправка ответа
        await send_responses(clean_text, amo_data, chat_id , photo_id)

        # Обновление CRM
        converse = await get_converse(list_ai)
        crm_data = await chat_history_sort(converse, amo_history)
        logger.info(f"CRM данные для обновления: {crm_data}")
        await send_message_to_group(crm_data)
        await update_field(entity_id, crm_data)


    except Exception as e:
        logger.error(f"Произошла ошибка при обработке: {e}", exc_info=True)


