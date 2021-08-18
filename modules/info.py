from src import IRCBot, IRCChannels, ModuleManager, utils
import os
import resource


DBVERSION = IRCBot.VERSION
SOURCEURL = "https://git.io/magicirc"


class Module(ModuleManager.BaseModule):
    @utils.hook("received.command.version")
    def version(self, event):
        commit = utils.git_commit(self.bot.directory)

        out = "Version: MagicBot %s" % DBVERSION
        # if not commit == None:
        #    branch, commit = commit
        #     out = "%s (%s@%s)" % (out, branch or "", commit)
        event["stdout"].write(out)

    @utils.hook("received.command.source")
    def source(self, event):
        event["stdout"].write("Source: MagicBot %s (%s)" %
                              (DBVERSION, SOURCEURL))

    @utils.hook("received.command.stats")
    def source(self, event):
        with open('/proc/self/status') as f:
            memusage = f.read().split('VmRSS:')[1].split('\n')[0][:-3]

        memusage = str(int(memusage.strip()) / 1024)[:6]

        servers = len(self.bot.servers)
        total_channels = 0

        for server in self.bot.servers.values():
            total_channels += len(server.get_channels())

        loaded_modules = self.bot.modules.list_modules(
            whitelist={}, blacklist={})

        total_modules = 0

        for module in loaded_modules:
            total_modules += 1

        print(total_modules)

        event["stdout"].write("Powered by MagicBot %s. Using %s MB RAM, Serving %d channel(s) across %d server(s) with %s loaded modules." % (
            DBVERSION, utils.irc.bold(memusage), total_channels, servers, utils.irc.bold(total_modules)))
