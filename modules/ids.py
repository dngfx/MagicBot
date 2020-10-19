#--depends-on commands

from src import ModuleManager, utils


class Module(ModuleManager.BaseModule):
    _name = "IDs"


    @utils.hook("received.command.myid")
    def my_id(self, event):
        """
        :help: Show your user ID
        """
        event["stdout"].write("%s: %d" % (utils.irc.bold(event["user"].nickname), event["user"].get_id()))


    @utils.hook("received.command.myaccount")
    @utils.kwarg("help", "Show what I think your account name is")
    def account(self, event):
        event["stdout"].write("Account name for %s: %s" %
                              (event["user"].nickname,
                               utils.irc.bold(self.exports.get_one("account-name")(event["user"]))))


    @utils.hook("received.command.channelid", channel_only=True)
    def channel_id(self, event):
        """
        :help: Show the current channel's ID
        """
        event["stdout"].write("%s: %d" % (utils.irc.bold(event["target"].name), event["target"].id))
