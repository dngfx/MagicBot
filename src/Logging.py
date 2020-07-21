import sys, pprint
from src import Database, utils
from loguru import logger
from logging import StreamHandler


class Logger(object):
    logger: None

    def __init__(self):
        self.set_logger()

    def set_logger(self):
        self.logger = logger.add(
            StreamHandler(sys.stdout),
            colorize=True,
            format="<b><green>[{time:HH:mm:ss!UTC}]</green> <level>[{level}]</level></b> <level>{message}</level>",
            level="INFO",
            catch=True,
            enqueue=True
        )

        for curlevel in ("TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"):
            CurrentLevel = logger.level(curlevel)
            color = CurrentLevel.color.replace("<bold>", "")
            logger.level(curlevel, color=color)

    def formatter(self, server, context, message):
        message = utils.irc.parse_format(message).replace("<", "\<")

        formatted_log = "[<m><b>%s</b></m>:<e><b>%s</b></e>] %s" % (server.capitalize(), context, message)
        return formatted_log

    def info(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(colors=True).info(message)
        return True

    def debug(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(colors=True).debug(message)
        return

    def warning(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(log=True).warning(message)
        return

    def warn(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(colors=True).warning(message)
        return

    def error(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(colors=True).error(message)
        return

    def critical(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(colors=True).critical(message)
        return

    def trace(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(colors=True).trace(message)
        return
