from src import IRCBot, ModuleManager, utils


DBVERSION = "v1.0.2"
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
        event["stdout"].write("Source: MagicBot %s (%s)" % (DBVERSION, SOURCEURL))
