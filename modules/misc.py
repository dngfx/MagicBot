#--depends-on commands
#--depends-on config

from src import ModuleManager, utils, random

# BORIS JOHNSON
BOJO_CHOICES = [
    "https://misconfigured.link/bojo/1.jpg",
    "https://misconfigured.link/bojo/2.jpg",
    "https://misconfigured.link/bojo/3.jpg",
    "https://misconfigured.link/bojo/4.jpg",
    "https://misconfigured.link/bojo/5.jpg",
    "https://misconfigured.link/bojo/6.jpg",
    "https://misconfigured.link/bojo/7.jpg",

]
# BORIS JOHNSON

@utils.export("channelset", utils.BoolSetting("jerkcity-enabled", "Is the jerkcity command enabled?"))

class Module(ModuleManager.BaseModule):
    JERKCITY_LIST = []
    _name = None

    @utils.hook("received.command.jerkcity", channel_only=True)
    def jerkcity(self, event):
        channel = event["channel"]
        if not channel.get_setting("jerkcity-enabled", False):
            return

        if not self.JERKCITY_LIST:
            jerkcity = open(self.bot.config["jerkcity-filename"])
            self.JERKCITY_LIST =jerkcity.read().splitlines()
            jerkcity.close()

        choice = random.choice(self.JERKCITY_LIST)
        channel.send_message("%s" % utils.irc.bold(choice))

    @utils.hook("received.command.bojo", alias_of="borisjohnson")
    @utils.hook("received.command.borisjohnson", channel_only=True)
    @utils.kwarg("help", "Receive an image of boris johnson")
    def decide(self, event):
        event["stdout"].prefix = "BORIS JOHNSON"
        event["stdout"].write("%s" % utils.irc.bold(random.choice(CHOICES)))

