#--depends-on config

from src import ModuleManager, utils


@utils.export("serverset", utils.Setting("bot-channel", "Set main channel", example="#dongbot"))
@utils.export("serverset", utils.Setting("testing-channel", "Set testing channel", example="#dongbot-test"))
@utils.export(
        "serverset", utils.BoolSetting("testing-enabled", "If debug/testing should be enabled in the testing channel")
)
@utils.export("serverset", utils.BoolSetting("join-testing-channel", "If the bot should join the testing channel"))
class Module(ModuleManager.BaseModule):


    @utils.hook("received.001")
    def do_join(self, event):
        bot_channel = event["server"].get_setting("bot-channel", self.bot.config.get("bot-channel", None))
        if not bot_channel == None:
            event["server"].send_join(bot_channel)

        test_channel = event["server"].get_setting("testing-channel", self.bot.config.get("testing-channel", None))
        join_test = event["server"].get_setting("join-testing-channel", False)

        if not test_channel == None and join_test == True:
            event["server"].send_join(test_channel)
