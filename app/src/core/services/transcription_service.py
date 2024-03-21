import os
import tempfile
from pathlib import Path
from typing import Dict, Any
from typing import List

from fastapi import Depends
from openai import OpenAI
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

from app.src.common.app_logging.logging import logger
from app.src.common.config.secret_manager import SecretManager
from app.src.core.services.base_service import BaseService


class TranscriptionService(BaseService):
    """
    Handles audio file transcription by splitting large files into smaller chunks,
    transcribing them individually, and then aggregating the results.

    Attributes:
        TEN_MINUTES (int): Duration in milliseconds to split the audio files.
    """
    TEN_MINUTES = 10 * 60 * 1000  # 10 minutes in milliseconds

    def __init__(
            self,
            secret_manager: SecretManager = Depends()
    ):
        """Initializes the TranscriptionService with base service name and OpenAI client."""
        super().__init__("TranscriptionService")
        openai_api_key = secret_manager.get_openai_secret()
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        else:
            logger.info(f"Openai api key found ******{openai_api_key[-3:]}")
        self.client = OpenAI(api_key=openai_api_key)

    def generate_transcription(self, media_path: Path) -> Dict[str, Any]:
        """
        Splits an audio file into chunks, transcribes each, and aggregates the results.

        Args:
            media_path (Path): Path to the audio file to transcribe.

        Returns:
            Dict[str, Any]: A dictionary containing the concatenated text and aggregated segments.

        Raises:
            Exception: General exceptions caught for logging and re-raising.
        """
        logger.info(f"Starting transcription for file: {media_path}")
        try:
            chunks = self.split_audio(media_path)
            aggregated_result = {"text": "", "segments": []}

            for index, chunk in enumerate(chunks, start=1):
                with tempfile.NamedTemporaryFile(delete=True, suffix=media_path.suffix) as temp_file:
                    # ffmpeg fails to export m4a chunks, It's recommended to use ipod format as an alternate
                    format = "ipod" if media_path.suffix.lstrip('.') == 'm4a' else media_path.suffix.lstrip('.')
                    chunk.export(temp_file.name, format=format)
                    with open(temp_file.name, 'rb') as media_chunk_file:
                        logger.debug(f"Transcribing chunk {index} of {len(chunks)}")
                        response = self.client.audio.transcriptions.create(
                            file=media_chunk_file,
                            model="whisper-1",
                            response_format="verbose_json",
                            prompt="",
                            timestamp_granularities=["segment"],
                        )
                        transcription = response.model_dump()
                        aggregated_result["text"] += transcription["text"] + " "
                        aggregated_result["segments"].extend(transcription["segments"])

            logger.info("Transcription completed successfully.")
            return aggregated_result
        except Exception as e:
            logger.error(f"Error during transcription of file {media_path}: {e}", exc_info=True)
            if media_path.exists():
                media_path.unlink()
            raise
        finally:
            if media_path.exists():
                media_path.unlink()

    def split_audio(self, media_path: Path) -> List[AudioSegment]:
        """
        Splits an audio file into 10-minute chunks.

        Returns:
            List[AudioSegment]: A list of audio segments.

        Raises:
            FileNotFoundError: If the provided media_path does not exist.
            CouldntDecodeError: If the provided media_path is not a valid audio file.
            Exception: If any other unexpected error occurs during the splitting process.
        """
        try:
            logger.info(f"Starting to split {media_path} into 10-minute chunks.")
            media = self._load_audio_file(media_path)
            chunks = self._split_into_chunks(media)
            logger.info(f"File {media_path} split into {len(chunks)} chunks.")
            return chunks
        except FileNotFoundError as e:
            logger.error(f"Error: {e}")
            raise
        except CouldntDecodeError as e:
            logger.error(f"Error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while splitting {media_path}: {e}")
            raise

    def _load_audio_file(self, media_path: Path) -> AudioSegment:
        """
        Loads an audio file from the provided path.

        Args:
            media_path (Path): Path to the audio file.

        Returns:
            AudioSegment: The loaded audio file.

        Raises:
            FileNotFoundError: If the provided media_path does not exist.
            CouldntDecodeError: If the provided media_path is not a valid audio file.
        """
        if not media_path.exists():
            raise FileNotFoundError(f"File not found: {media_path}")

        try:
            logger.debug(f"Loading audio file: {media_path}")
            return AudioSegment.from_file(media_path)
        except CouldntDecodeError as e:
            raise CouldntDecodeError(f"Error decoding audio file: {media_path}") from e

    def _split_into_chunks(self, media: AudioSegment) -> List[AudioSegment]:
        """
        Splits an audio file into 10-minute chunks.

        Args:
            media (AudioSegment): The audio file to split.

        Returns:
            List[AudioSegment]: A list of audio segments.
        """
        chunks = []
        start, end = 0, self.TEN_MINUTES

        while True:
            chunk = media[start:end]
            if not chunk:
                break
            chunks.append(chunk)
            start, end = end, end + self.TEN_MINUTES

        logger.debug(f"File split into {len(chunks)} chunks.")
        return chunks


if __name__ == "__main__":
    audio_file_path = Path('/Users/rachakonda/Work/Callensights/backends/audio/record_3.m4a')
    transcription_service = TranscriptionService()
    result = transcription_service.generate_transcription(media_path=audio_file_path)
    print("Transcription Result:\n", result)
