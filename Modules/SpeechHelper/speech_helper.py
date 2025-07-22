import os
import requests
from Modules.OpenAI.openai_client import OpenAIClient

class SpeechHelper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpeechHelper, cls).__new__(cls)
        return cls._instance

    async def transcribe_voice(self, voice_file_path: str) -> str:
        with open(voice_file_path, "rb") as file:
            transcription = OpenAIClient.get_instance().client.audio.transcriptions.create(
                model="whisper-1",
                file=file
            )
        return transcription.text

    async def text_to_speech(self, text: str, output_path: str) -> None:
        speech_response = OpenAIClient.get_instance().client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        with open(output_path, 'wb') as f:
            f.write(speech_response.content)

    async def download_voice_file(self, file_path: str, output_path: str) -> None:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'wb') as f:
            response = requests.get(file_path)
            f.write(response.content) 