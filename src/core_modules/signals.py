import signal
import sys

from src import IRCLine, ModuleManager
from src.Logging import Logger as log


class Module(ModuleManager.BaseModule):
    def on_load(self):
        self._exited = False
        signal.signal(signal.SIGINT, self.SIGINT)
        signal.signal(signal.SIGUSR1, self.SIGUSR1)
        signal.signal(signal.SIGHUP, self.SIGHUP)

    def SIGINT(self, signum, frame):
        print()
        self.bot.trigger(lambda: self._kill(signum))

    def _kill(self, signum):
        if self._exited:
            return
        self._exited = True

        self.events.on("signal.interrupt").call(signum=signum)

        written = False
        for server in list(self.bot.servers.values()):
            if server.connected:
                server.socket.clear_send_buffer()

                line = IRCLine.ParsedLine("QUIT", ["Shutting down"])
                sent_line = server.send(line, immediate=True)
                sent_line.events.on("send").hook(self._make_hook(server))

                server.send_enabled = False
                written = True

        if not written:
            sys.exit()

    def _make_hook(self, server):
        return lambda e: self._disconnect_hook(server)

    def _disconnect_hook(self, server):
        self.bot.disconnect(server)
        if not self.bot.servers:
            sys.exit()

    def SIGUSR1(self, signum, frame):
        self.bot.trigger(self._reload_config)

    def SIGHUP(self, signum, frame):
        self.bot.trigger(self._SIGHUP)

    def _SIGHUP(self):
        self._reload_config()
        self._reload_modules()

    def _reload_config(self):
        log.info()
        self.bot.config.load()
        log.info()

    def _reload_modules(self):
        log.info()

        result = self.bot.try_reload_modules()
        if result.success:
            log.info()
        else:
            log.warn(message=result.message)
