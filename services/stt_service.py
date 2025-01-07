import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class STTService:
    def __init__(self):
        self.client = OpenAI()

    def transcribe(self, url, model="whisper-1"):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            audio_content = response.content
            try:
                transcript = self.client.audio.transcriptions.create(
                    model=model,
                    file=("audio_file.m4a", audio_content)
                )
                return transcript.text
            except Exception as e:
                print(f"Ошибка транскрибирования: {e}")
                return None
        else:
            print("Ошибка при скачивании аудиофайла")
            return None
