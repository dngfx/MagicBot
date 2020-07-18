import pydle, sys
from src import Database, utils
from loguru import logger
from logging import StreamHandler


class Logger(object):

    def set_logger(self):
        logger.add(
            StreamHandler(sys.stdout),
            colorize=True,
            format="<green>[{time:HH:mm:ss!UTC}]</green> — <level>[{level}]</level> — <level>{message}</level>",
            level="INFO",
            catch=True,
            enqueue=True
        )

    def info(self, message):
        logger.opt(colors=True).info(message)
        return

    def debug(self, message):
        logger.opt(colors=True).debug(message)
        return

    def success(self, message):
        logger.opt(colors=True).success(message)
        return

    def warning(self, message):
        logger.opt(colors=True).warning(message)
        return

    def warn(self, message):
        logger.opt(colors=True).warning(message)
        return

    def error(self, message):
        logger.opt(colors=True).error(message)
        return

    def critical(self, message):
        logger.opt(colors=True).critical(message)
        return

    def trace(self, message):
        logger.opt(colors=True).trace(message)
        return
