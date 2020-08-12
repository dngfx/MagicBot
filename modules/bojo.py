#--depends-on commands

import random

from src import ModuleManager, utils


CHOICES = [
    "https://i.imgur.com/xkaaN4S.png",
    "https://i.imgur.com/3ju3iZC.png",
    "https://i.imgur.com/sgGTqw8.png",
    "https://i.imgur.com/8wqcihc.png",
    "https://i.imgur.com/1C7cCJs.png",
    "https://i.imgur.com/MpnrZSB.png",
    "https://i.imgur.com/74c8wdk.jpg",
    "https://i.imgur.com/MtzwbtJ.jpg",
    "https://i.imgur.com/7gql1IN.jpg",
    "https://i.imgur.com/UAsmjLD.jpg"
]


class Module(ModuleManager.BaseModule):
    _name = "BORIS JOHNSON"


    @utils.hook("received.command.bojo", alias_of="borisjohnson")
    @utils.hook("received.command.borisjohnson")
    @utils.kwarg("help", "Receive an image of boris johnson")
    def decide(self, event):
        event["stdout"].write("%s" % utils.irc.bold(random.choice(CHOICES)))
