from enum import Enum


class BackgroundStageEnum(Enum):
    TRANSCRIPTION: str = 'TRANSCRIPTION'
    FEEDBACK: str = 'FEEDBACK'


class BackgroundTaskStatusEnum(Enum):
    SUCCESS: str = "SUCCESS"
    FAILED: str = "FAILED"
