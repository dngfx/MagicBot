# --depends-on commands

from src import ModuleManager, utils


@utils.export(
    "channelset",
    utils.BoolSetting("echo-enabled", "Is the echo/action/msg command enabled?"),
)
class Module(ModuleManager.BaseModule):
    @utils.hook("received.command.echo", channel_only=True)
    @utils.kwarg("remove_empty", False)
    @utils.kwarg("help", "Echo a string back")
    @utils.spec("!<message>string")
    def echo(self, event):
        channel = event["target"]
        if not channel.get_setting("echo-enabled", True):
            return

        event["stdout"].write(event["spec"][0])

    @utils.hook("received.command.action", channel_only=True)
    @utils.kwarg("remove_empty", False)
    @utils.kwarg("help", "Make the bot send a /me")
    @utils.spec("!<message>string")
    def action(self, event):
        channel = event["target"]
        if not channel.get_setting("echo-enabled", True):
            return

        event["target"].send_message("\x01ACTION %s\x01" % event["spec"][0])

    @utils.hook("received.command.msg", channel_only=True)
    @utils.kwarg("permission", "say")
    @utils.kwarg("remove_empty", False)
    @utils.kwarg("help", "Send a message to a target")
    @utils.spec("!<target>word !<message>string")
    def msg(self, event):
        channel = event["target"]
        if not channel.get_setting("echo-enabled", True):
            return

        event["server"].send_message(event["spec"][0], event["spec"][1])
