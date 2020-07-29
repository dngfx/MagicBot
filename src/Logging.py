import sys, pprint
from src import Database, utils
from loguru import logger
from logging import StreamHandler


class Logger(object):

    def __init__(self, log_level="INFO"):
        self.set_logger(log_level)

    def set_logger(self, log_level):
        self.logger = logger.add(
            StreamHandler(sys.stdout),
            colorize=True,
            format=
            "<b><green>[{time:HH:mm:ss!UTC}]</green> {function} <level>[{level}]</level></b> <level>{message}</level>",
            level=log_level
        )

        for curlevel in ("TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"):
            CurrentLevel = logger.level(curlevel)
            color = CurrentLevel.color.replace("<bold>", "")
            logger.level(curlevel, color=color)

    def formatter(self, server, context, message):
        message = utils.irc.parse_format(message)

        formatted_log = "[<m><b>%s</b></m>:<e><b>%s</b></e>] %s" % (server.capitalize(), context, message)
        return formatted_log

    def info(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(colors=True, depth=1).info(message)
        return True

    def debug(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(colors=True, depth=1).debug(message)
        return True

    def warning(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(log=True).warning(message)
        return True

    def warn(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(colors=True).warning(message)
        return True

    def error(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(colors=True).error(message)
        return True

    def critical(self, message="", server="", context="", format=False, **kwargs):
        logger.opt(colors=False).critical(message, **kwargs)
        return True

    def trace(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(colors=True).trace(message)
        return True
