from pathlib import Path
from typing import Any, List

from openai import OpenAI
from pydub import AudioSegment

from app.src.core.services.base_service import BaseService


class TranscriptionService(BaseService):
    def __init__(
            self
    ):
        super().__init__("Transcription")
        self.client = OpenAI()
        self.ten_mins = 10 * 60 * 1000  # 10 mins media

    def generate_transcription(self, media_path: Path) -> str:
        chunks = self.split_audio(media_path)
        for chunk in chunks:
            chunk.export("file.m4a")
            with open("file.m4a", 'rb') as media_chunk_file:
                self.client.audio.transcriptions.create(
                    media_chunk_file,
                    model="whisper-1",
                    response_format="json"
                )

    def split_audio(self, media_path: Path) -> List[Any]:
        media = AudioSegment.from_file(media_path)
        start = 0
        end = self.ten_mins
        chunks = []
        while True:
            media_chunk = media[start:end]
            if not media_chunk:
                break
            chunks.append(media_chunk)
            start = end
            end += self.ten_mins
        return chunks
