#--depends-on commands

import re, random
from src import ModuleManager, utils

STARSIGNS = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces"
]

STARSIGN_URL = "https://horoscope-api.herokuapp.com/horoscope/today/%s"


class Module(ModuleManager.BaseModule):

    @utils.hook("received.command.horoscope")
    @utils.kwarg("help", "Get your daily horoscope")
    @utils.kwarg("min_args", 1)
    @utils.spec("!<starsign>lstring")
    def wikipedia(self, event):
        sign = event["spec"][0].lower()

        if sign not in STARSIGNS:
            starsigns = ", ".join(STARSIGNS)
            event["stderr"].write("Invalid Starsigns. Valid starsigns are: %s" % starsigns)

        page = utils.http.request(STARSIGN_URL % sign).json()

        event["stdout"].write("%s: %s" % (utils.irc.bold("Today's Horoscope for " + sign.capitalize()),
                                          page["horoscope"]))
