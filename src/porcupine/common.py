import logging
from loguru import logger
import urllib3
import socket


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(level: str = "INFO"):
    urllib3.disable_warnings()
    logging.basicConfig(handlers=[InterceptHandler()], level=level)


def get_hostname() -> str:
    return socket.gethostbyname(socket.gethostname())
