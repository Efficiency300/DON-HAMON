from fastapi import FastAPI, Request
import asyncio
from urllib.parse import parse_qs
import uvicorn
from server.message_buffer import BufferManager
from status_crm.stage_info import stage_info


app = FastAPI()
AI_OTVECHAET = 72349674
NERAZOBRANOE = 72349670
buffer_manager = BufferManager()

@app.post("/")
async def client_data(r: Request):
    try:
        raw_body = await r.body()
        decoded_body = raw_body.decode("utf-8")
        parsed_data = parse_qs(decoded_body)

        message_text = parsed_data.get("message[add][0][text]", [""])[0]
        chat_id = parsed_data.get("message[add][0][chat_id]", [""])[0]
        talk_id = parsed_data.get("message[add][0][talk_id]", [""])[0]
        current_time = int(parsed_data.get("message[add][0][created_at]", ["0"])[0])
        lead_id = parsed_data.get("message[add][0][entity_id]", [None])[0]
        attachment_type = parsed_data.get("message[add][0][attachment][type]", [None])[0]
        attachment_link = parsed_data.get("message[add][0][attachment][link]", [None])[0]
        result = attachment_link if attachment_type in ["voice", "picture"] else ""
     
        if not chat_id or (not message_text and not attachment_link):
            return {"error": "Invalid data"}

        if message_text:
            await buffer_manager.add_to_buffer(chat_id, message_text)
        if attachment_link:
            if await buffer_manager.is_image(attachment_link):
                await buffer_manager.add_to_buffer(chat_id, {"type": "image", "content": attachment_link})
            elif await buffer_manager.is_voice(attachment_link):
                await buffer_manager.add_to_buffer(chat_id, {"type": "voice", "content": attachment_link})

        results = await stage_info(lead_id)
        if results in [NERAZOBRANOE]:
            if chat_id not in buffer_manager.user_timers or buffer_manager.user_timers[chat_id].done():
                buffer_manager.user_timers[chat_id] = asyncio.create_task(
                    buffer_manager.process_target_audience(chat_id, lead_id, talk_id, result, current_time)
                )

        if results in [AI_OTVECHAET]:
            check_result = await buffer_manager.check_and_return(talk_id, current_time, result, lead_id)
            if check_result:
                return check_result

            if chat_id not in buffer_manager.user_timers or buffer_manager.user_timers[chat_id].done():
                buffer_manager.user_timers[chat_id] = asyncio.create_task(
                    buffer_manager.start_processing(chat_id, lead_id)
                )
            await buffer_manager.db.add(talk_id, current_time)
            return {"status": "success", "data": {"result": result, "entity_id": lead_id}}

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2020)
