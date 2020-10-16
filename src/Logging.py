import logging
import sys

from loguru import logger as log

from src import utils


def formatter(server="", context="Server", message=""):
    context = "Server" if context == "" else context
    server = "Startup" if server == "" else server

    message = utils.irc.parse_format(message)
    #context = "<m><b>%s</b></m>:<e><b>%s</b></e>" % (server, context)
    return [server, context, message]


class Logger(object):

    def __init__(self, log_level="INFO"):
        print("Init log level at: %s" % log_level)
        log_level = log_level.upper()

        log.add(
                logging.StreamHandler(sys.stdout),
                colorize=True,
                format=
                "<b><green>[{time:HH:mm:ss!UTC}]</green> {function: <20} <level>[ {level: ^7} ]</level></b> [ <m><b>{extra[server]}</b></m>:<e><b>{extra[context]}</b></e>{extra[padding]} ] <level>{message}</level>",
                level=log_level
        )

        self.set_log_colours()

    @staticmethod
    def set_log_colours():
        for lev in ("TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"):
            current_level = log.level(lev)
            color = current_level.color.replace("<bold>", "")
            log.level(name=lev, color=color)

    @staticmethod
    def get_log(self: log):
        return log

    @staticmethod
    def info(message="", server="", context="", formatting=False):
        if formatting:
            server, context, message = formatter(server, context, message)
        formatted_len = " " * (len(server) + len(context))
        log.padding = max(0, (20 - len(formatted_len)))
        context = {"server": server, "context": context, "padding": " " * log.padding}
        log.bind(**context).opt(colors=True, depth=1).log("INFO", message)
        return True

    @staticmethod
    def success(message="", server="", context="", formatting=False):
        if formatting:
            server, context, message = formatter(server, context, message)
        formatted_len = " " * (len(server) + len(context))
        log.padding = max(0, (20 - len(formatted_len)))
        context = {"server": server, "context": context, "padding": " " * log.padding}
        log.bind(**context).opt(colors=True, depth=1).log("SUCCESS", message)
        return True

    @staticmethod
    def debug(message="", server="", context="", formatting=True):
        if formatting:
            server, context, message = formatter(server, context, message)
        formatted_len = " " * (len(server) + len(context))
        log.padding = max(0, (20 - len(formatted_len)))
        context = {"server": server, "context": context, "padding": " " * log.padding}
        log.level("DEBUG")
        log.bind(**context).opt(colors=True, depth=1).log("DEBUG", message)
        return True

    @staticmethod
    def warning(message="", server="", context="", formatting=False):
        if formatting:
            server, context, message = formatter(server, context, message)
        formatted_len = " " * (len(server) + len(context))
        log.padding = max(0, (20 - len(formatted_len)))
        context = {"server": server, "context": context, "padding": " " * log.padding}
        log.bind(**context).opt(colors=True, depth=1).log("WARNING", message)
        return True

    warn = warning

    @staticmethod
    def error(message="", server="", context="", formatting=False):
        if formatting:
            server, context, message = formatter(server, context, message)
        formatted_len = " " * (len(server) + len(context))
        log.padding = max(0, (20 - len(formatted_len)))
        context = {"server": server, "context": context, "padding": " " * log.padding}
        log.bind(**context).opt(colors=True, depth=1).log("ERROR", message)
        return True

    @staticmethod
    def critical(message="", server="", context="", formatting=False):
        log.opt(colors=False).log("CRITICAL", message)
        return True

    @staticmethod
    def trace(message="", server="", context="", formatting=False):
        if formatting:
            server, context, message = formatter(server, context, message)
        log.log("TRACE", message)
        return True
