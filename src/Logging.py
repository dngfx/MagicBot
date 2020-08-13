import logging
import sys

from loguru import logger as log

from src import utils


class Logger(object):
    loggen = log.add(
            logging.StreamHandler(sys.stdout),
            colorize=True,
            format=
            "<b><green>[{time:HH:mm:ss!UTC}]</green> {function: <20} <level>[ {level: ^7} ]</level></b> [ <m><b>{extra[server]}</b></m>:<e><b>{extra[context]}</b></e>{extra[padding]} ] <level>{message}</level>",
            level="INFO"
    )


    def __init__(self):
        self.set_log()


    def set_log(self):
        for curlevel in ("TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"):
            CurrentLevel = log.level(curlevel)
            color = CurrentLevel.color.replace("<bold>", "")
            log.level(curlevel, color=color)


    def get_log(self):
        return log


    def formatter(self, server="", context="Server", message=""):
        context = "Server" if context == "" else context
        server = "Startup" if server == "" else server

        message = utils.irc.parse_format(message)
        #context = "<m><b>%s</b></m>:<e><b>%s</b></e>" % (server, context)
        return [server, context, message]


    def info(self=log, message="", server="", context="", formatting=False):
        if formatting:
            server, context, message = Logger.formatter(self, server, context, message)
        formatted_len = " " * (len(server) + len(context))
        log.padding = max(0, (20 - len(formatted_len)))
        context = {"server": server, "context": context, "padding": " " * log.padding}
        log.bind(**context).opt(colors=True, depth=1).info(message)
        return True


    def debug(self=log, message="", server="", context="", formatting=False):
        if formatting:
            server, context, message = Logger.formatter(self, server, context, message)
        formatted_len = " " * (len(server) + len(context))
        log.padding = max(0, (20 - len(formatted_len)))
        context = {"server": server, "context": context, "padding": " " * log.padding}
        log.bind(**context).opt(colors=True, depth=1).debug(message)
        return True


    def warning(self=log, message="", server="", context="", formatting=False):
        if formatting:
            server, context, message = Logger.formatter(self, server, context, message)
        formatted_len = " " * (len(server) + len(context))
        log.padding = max(0, (20 - len(formatted_len)))
        context = {"server": server, "context": context, "padding": " " * log.padding}
        log.bind(**context).opt(colors=True, depth=1).warning(message)
        return True


    def warn(self=log, message="", server="", context="", formatting=False):
        if formatting:
            server, context, message = Logger.formatter(self, server, context, message)
        formatted_len = " " * (len(server) + len(context))
        log.padding = max(0, (20 - len(formatted_len)))
        context = {"server": server, "context": context, "padding": " " * log.padding}
        log.bind(**context).opt(colors=True, depth=1).warning(message)
        return True


    def error(self=log, message="", server="", context="", formatting=False):
        if formatting:
            context, message = Logger.formatter(self, server, context, message)
        log.error(message)
        return True


    def critical(self=log, message="", server="", context="", formatting=False, **kwargs):
        log.opt(colors=False).critical(message, **kwargs)
        return True


    def trace(self=log, message="", server="", context="", formatting=False):
        if formatting:
            context, message = Logger.formatter(self, server, context, message)
        log.trace(message)
        return True
