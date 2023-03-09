# coding:utf-8
import logging
import os
from itertools import chain
import sys
from types import FrameType
from typing import cast

from loguru import logger

LOGGING__FILE__ = "logging%s__init__.py" % os.path.sep


class InterceptHandler(logging.Handler):
    """Logs to loguru from Python logging module"""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while self.issame(frame.f_code.co_filename, logging.__file__):  # logging.__file__ noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )

    def issame(self, co_filename, logging_filename):
        if logging_filename.endswith("pyc"):
            return co_filename == LOGGING__FILE__
        return co_filename == logging_filename


def setup_loguru_logging_intercept(
        level=logging.DEBUG, modules=(), info_log_file="info.log", err_log_file="error.log"
):
    logging.basicConfig(handlers=[InterceptHandler()], level=level)  # noqa
    for logger_name in chain(("",), modules):
        mod_logger = logging.getLogger(logger_name)
        mod_logger.handlers = [InterceptHandler(level=level)]
        mod_logger.propagate = False
    logger.configure(handlers=[
        {
            "sink": sys.stdout,
            "level": level,
            # "format": "<green>{time:YYYY-mm-dd HH:mm:ss.SSS}</green> | {thread.name} | <level>{level}</level> | <cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        },
        {
            "sink": info_log_file,
            "level": level,
            "rotation": "10 MB",
            "retention": "1 week",
            "encoding": 'utf-8',
            # "format": "{time:YYYY-mm-dd HH:mm:ss.SSS} | {thread.name} | {level} | {module} : {function}:{line} -  {message}"
        },
        {
            "sink": err_log_file,
            "serialize": True,
            "level": 'ERROR',
            "retention": "1 week",
            "rotation": "10 MB",
            "encoding": 'utf-8',
            # "format": "{time:YYYY-mm-dd HH:mm:ss.SSS} | {thread.name} | {level} | {module} : {function}:{line} -  {message}"
        },
    ])
