import logging

from app.src.common.config import SERVICE_NAME


class AppFilter(logging.Filter):
    def filter(self, record):
        record.service = SERVICE_NAME
        return True
