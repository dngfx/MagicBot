#--depends-on commands

import random

from src import ModuleManager, utils


CHOICES = [
    "https://misconfigured.link/bojo/1.jpg",
    "https://misconfigured.link/bojo/2.jpg",
    "https://misconfigured.link/bojo/3.jpg",
    "https://misconfigured.link/bojo/4.jpg",
    "https://misconfigured.link/bojo/5.jpg",
    "https://misconfigured.link/bojo/6.jpg",
    "https://misconfigured.link/bojo/7.jpg",

]


class Module(ModuleManager.BaseModule):
    _name = "BORIS JOHNSON"


    @utils.hook("received.command.bojo", alias_of="borisjohnson")
    @utils.hook("received.command.borisjohnson")
    @utils.kwarg("help", "Receive an image of boris johnson")
    def decide(self, event):
        event["stdout"].write("%s" % utils.irc.bold(random.choice(CHOICES)))
