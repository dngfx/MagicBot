#--depends-on config
#--depends-on format_activity

import datetime
from src import EventManager, ModuleManager, utils
from src.Logging import Logger as log
import pprint


@utils.export("botset", utils.BoolSetting("print-motd", "Set whether I print /motd"))
@utils.export("botset", utils.BoolSetting("pretty-activity", "Whether or not to pretty print activity"))
# Used to migrate word stats from prior to v1.19.0
@utils.export("channelset", utils.BoolSetting("print", "Whether or not to print activity a channel to logs"))
class Module(ModuleManager.BaseModule):

    def _print(self, event):
        if True != True:  # (event["channel"] and not event["channel"].get_setting("print", True)):
            return

        line = event["line"]
        if event["pretty"] and self.bot.get_setting("pretty-activity", False):
            line = event["pretty"]

        server = event["server"].alias

        context = ("%s" % event["context"]) if (event["context"] not in ["*", ""]) else "Server"

        log.info(log, message=line, server=server, context=context, format=True)

    @utils.hook("formatted.message.channel")
    @utils.hook("formatted.notice.channel")
    @utils.hook("formatted.notice.private")
    @utils.hook("formatted.join")
    @utils.hook("formatted.part")
    @utils.hook("formatted.nick")
    @utils.hook("formatted.invite")
    @utils.hook("formatted.mode.channel")
    @utils.hook("formatted.topic")
    @utils.hook("formatted.topic-timestamp")
    @utils.hook("formatted.kick")
    @utils.hook("formatted.quit")
    @utils.hook("formatted.rename")
    @utils.hook("formatted.chghost")
    @utils.hook("formatted.account")
    @utils.hook("formatted.delete")
    def formatted(self, event):
        self._print(event)

    @utils.hook("formatted.motd")
    def motd(self, event):
        if self.bot.get_setting("print-motd", True):
            self._print(event)
