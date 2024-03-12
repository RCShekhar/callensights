from app.src.core.services.base_service import BaseService


class FeedbackService(BaseService):
    def __init__(self) -> None:
        super().__init__("Feedback")

    def generate_feedback(self, media_code: str) -> str:
        pass
