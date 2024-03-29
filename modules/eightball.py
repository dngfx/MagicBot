# --depends-on commands

import random

from src import ModuleManager, utils


CHOICES = [
    "Definitely",
    "For Sure",
    "Yes",
    "Yeah",
    "I think so",
    "Probably",
    "Maybe",
    "Probably not",
    "No",
    "Not a chance",
    "Definitely not",
    utils.irc.underline(utils.irc.italic(
        utils.irc.color("P e r h a p s", utils.consts.GREEN))),
    "I don't know",
    "Ask again later",
    "The answer is unclear",
    "Absolutely",
    "Dubious at best",
    "As I see it, yes",
    "It is certain",
    "Naturally",
    "Reply hazy, try again later",
    "Hmm... Could be!",
    "I'm leaning towards no",
    "Without a doubt",
    "Sources say no",
    "Sources say yes",
    "Sources say maybe",
]


class Module(ModuleManager.BaseModule):
    _name = "8Ball"

    @ utils.hook("received.command.8", alias_of="8ball")
    @ utils.hook("received.command.8ball", min_args=1)
    @ utils.kwarg("help", "Ask the mystic 8ball a question")
    @ utils.kwarg("usage", "<question>")
    def decide(self, event):
        event["stdout"].write(
            "You shake the magic ball... it says %s"
            % utils.irc.bold(random.choice(CHOICES))
        )
