import asyncio
import random
from collections import defaultdict
import json
from services.photo_service import PhotoService
from services.stt_service import STTService
from status_crm.change_funnel import change_funnel
from services.target_audience import target_audience
from core.process_messages import process_messages
from status_crm.stage_info import stage_info
from handlers.JsonDataBase import JSONDatabase
from pathlib import Path
from typing import Dict, List , Union, Optional

import logging

BASE_DIR = Path(__file__).resolve().parent.parent
TALK_ID_JSON_PATH = BASE_DIR / "config/talk_id.json"
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

AI_OTVECHAET = 72349674
NERAZOBRANOE = 72349670
class BufferManager:
    def __init__(self, rand_first=8):
        self.user_buffers: Dict[str, List[Dict[str, str] | str]] = defaultdict(list)
        self.user_timers = {}
        self.rand_first = rand_first
        self.db = JSONDatabase(TALK_ID_JSON_PATH)
        self.photo_service = PhotoService()
        self.stt_service = STTService()

    @staticmethod
    async def is_image(url: str) -> bool:
        return isinstance(url, str) and url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))

    @staticmethod
    async def is_voice(url: str) -> bool:
        return isinstance(url, str) and url.lower().endswith((".m4a", ".mp3", ".wav", ".ogg"))
    async def add_to_buffer(self, chat_id: str, data: Union[Dict[str, str], str]) -> None:
        self.user_buffers[chat_id].append(data)

    async def check_and_return(self, talk_id: str, current_time: int, result: str, entity_id: str) -> Optional[dict]:
        past_time = await self.db.get(talk_id)
        if past_time and int(past_time) >= current_time:
            return {"status": "success", "data": {"result": result, "entity_id": entity_id}}
        return None




    async def process_attachments(self, chat_id: str) -> tuple[str, str , str]:
        image_description = ""
        transcribed_text = ""
        processed_text_parts = []


        for msg in self.user_buffers.pop(chat_id, []):
            if isinstance(msg, dict):
                if msg.get("type") == "image":
                    image_url = msg.get("content")
                    image_response = await self.photo_service.process_image_from_url(image_url)
                    if image_response:
                        image_data = json.loads(image_response)
                        image_description += f"\n\nКонтекст изображения: {image_data.get('description', '')}"
                elif msg.get("type") == "voice":
                    voice_url = msg.get("content")
                    transcribed = self.stt_service.transcribe(voice_url)
                    if transcribed:
                        transcribed_text += f"\n\nТранскрибированное голосовое сообщение: {transcribed}"
            else:
                processed_text_parts.append(msg)

        return "\n".join(processed_text_parts), image_description, transcribed_text

    async def process_target_audience(self, chat_id: str, entity_id: str, talk_id: str, result: str, current_time: int) -> Optional[dict]:
        try:
            await asyncio.sleep(random.randint(5, self.rand_first))
            combined_data = await self.process_attachments(chat_id)
            results = await stage_info(entity_id)

            if results in [NERAZOBRANOE]:
                target_id = await target_audience(combined_data)
                print(target_id['funnel'], target_id['id'])
                await asyncio.sleep(10)
                await change_funnel(entity_id, int(target_id['funnel']), int(target_id['id']))
                resuts = await stage_info(entity_id)
                if resuts in [72349674]:
                    check_result = await self.check_and_return(talk_id, current_time, result, entity_id)
                    if check_result:
                        return check_result
                    await process_messages(chat_id, entity_id, combined_data)
                    await self.db.add(talk_id, current_time)
                return {"status": "success", "message": "User status updated"}

            self.user_buffers.pop(chat_id, None)
            self.user_timers.pop(chat_id, None)

        except Exception as e:
            print(f"Error processing {chat_id}: {e}")

    async def start_processing(self, chat_id: str, entity_id: str) -> None:
        try:
            await asyncio.sleep(random.randint(2, self.rand_first))
            combined_data = await self.process_attachments(chat_id)
            await process_messages(chat_id, entity_id, combined_data)
            self.user_buffers.pop(chat_id, None)
            self.user_timers.pop(chat_id, None)
        except Exception as e:
            logger.error(f"Error starting processing for {chat_id}: {e}")
