import logging

from app.src.common.app_logging.filter import AppFilter
from app.src.common.app_logging.logging_handlers import cw_handler
from app.src.common.config import SERVICE_NAME
from app.src.common.config import LOG_FORMAT

logger = logging.getLogger(SERVICE_NAME)
logger.addFilter(AppFilter())
formatter = logging.Formatter(LOG_FORMAT)
console_handler = logging.StreamHandler()

logger.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
cw_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(cw_handler)
