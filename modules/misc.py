#--depends-on commands
#--depends-on config

from src import ModuleManager, utils
import random

# BORIS JOHNSON
BOJO_CHOICES = [
    "https://misconfigured.link/bojo/1.jpg",
    "https://misconfigured.link/bojo/2.jpg",
    "https://misconfigured.link/bojo/3.jpg",
    "https://misconfigured.link/bojo/4.jpg",
    "https://misconfigured.link/bojo/5.jpg",
    "https://misconfigured.link/bojo/6.jpg",
    "https://misconfigured.link/bojo/7.jpg",
    "https://misconfigured.link/bojo/8.jpg",
    "https://misconfigured.link/bojo/9.jpg",
    "https://misconfigured.link/bojo/10.jpg",

]

BOJO_URL = "https://misconfigured.link/bojo/index.php"
# BORIS JOHNSON

@utils.export("channelset", utils.BoolSetting("jerkcity-enabled", "Is the jerkcity command enabled?"))
@utils.export("channelset", utils.BoolSetting("bojo-enabled", "Is the bojo command enabled?"))

class Module(ModuleManager.BaseModule):
    JERKCITY_LIST = []
    _name = None

    @utils.hook("received.command.jerkcity", channel_only=True)
    def jerkcity(self, event):
        channel = event["target"]

        if not channel.get_setting("jerkcity-enabled", False):
            return

        if len(self.JERKCITY_LIST) == 0:
            jerkcity = open(self.bot.config["jerkcity-filename"])
            self.JERKCITY_LIST =jerkcity.read().splitlines()
            jerkcity.close()

        choice = random.choice(self.JERKCITY_LIST)
        channel.send_message("%s" % utils.irc.bold(choice))

    @utils.hook("received.command.bojo", alias_of="borisjohnson")
    @utils.hook("received.command.borisjohnson", channel_only=True)
    @utils.kwarg("help", "Receive an image of boris johnson")
    def bojo(self, event):

        channel = event["target"]
        if not channel.get_setting("bojo-enabled", False):
            return

        args = {
            "imagelist": "true"
        }

        page = utils.http.request(BOJO_URL, get_params=args).json()

        event["stdout"].prefix = "BORIS JOHNSON"
        event["stdout"].write("%s" % utils.irc.bold(random.choice(page)))

    @utils.hook("received.command.hug", channel_only=True)
    @utils.kwarg("help", "hug or send a hug")
    @utils.spec("?<ruser>user")
    def hug_user(self, event):
        channel = event["target"]
        user = event["spec"][0]
        if user is None:
            user = event["user"].nickname

        channel.send_message("\x01ACTION hugs %s\x01" % user)
