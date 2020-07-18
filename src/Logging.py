import pydle, sys
from src import Database, utils
from loguru import logger


class Logger(object):

    def set_logger(self):
        logger.add(
            sys.stdout,
            colorize=True,
            format=
            "<green>[{time:HH:mm:ss!UTC}]</green> — <le>{name}: {line}</le> — <level>[{level}]</level> — <level>{message}</level>",
            level="INFO",
            catch=True,
            enqueue=True
        )

    def info(self, message):
        logger.opt(colors=True).info(message)

    def debug(self, message):
        logger.opt(colors=True).debug(message)

    def success(self, message):
        logger.opt(colors=True).success(message)

    def warning(self, message):
        logger.opt(colors=True).warning(message)

    def warn(self, message):
        logger.opt(colors=True).warning(message)

    def error(self, message):
        logger.opt(colors=True).error(message)

    def critical(self, message):
        logger.opt(colors=True).critical(message)

    def trace(self, message):
        logger.opt(colors=True).trace(message)
