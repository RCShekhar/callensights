from enum import Enum


class BackgroundStageEnum(str, Enum):
    TRANSCRIPTION: str = 'TRANSCRIPTION'
    FEEDBACK: str = 'FEEDBACK'


class BackgroundTaskStatusEnum(str, Enum):
    SUCCESS: str = "SUCCESS"
    FAILED: str = "FAILED"
