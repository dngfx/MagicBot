import sys
from src import Database, utils
from loguru import logger
from logging import StreamHandler


class Logger(object):

    def set_logger(self):
        logger.add(
            StreamHandler(sys.stdout),
            colorize=True,
            format="<green>[{time:HH:mm:ss!UTC}]</green> <level>[{level}]</level> — <level>{message}</level>",
            level="INFO",
            catch=True,
            enqueue=True
        )

    def formatter(self, server, context, message):
        message = utils.irc.parse_format(message).replace("<", "\<")
        formatted_log = "[<m>%s</m>:<e>%s</e>] %s" % (server.capitalize(), context, message)
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

    def success(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(colors=True).success(message)
        return

    def warning(self, message="", server="", context="", format=False):
        if format == True:
            message = Logger.formatter(Logger, server, context, message)
        logger.opt(colors=True).warning(message)
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
