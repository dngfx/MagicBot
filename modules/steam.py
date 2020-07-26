#--depends-on commands
#--depends-on config
#--depends-on permissions
#--require-config steam-api-key

import time, math, pprint
from steam import webapi, steamid
from steam.steamid import steam64_from_url
from src import EventManager, ModuleManager, utils, IRCChannel


@utils.export("set", utils.Setting("steamid", "Set your steam id", example="103582791429521412"))
class Module(ModuleManager.BaseModule):

    def _account_from_nick(self, event, nick):
        if not event["server"].has_user_id(nick):
            return False

        user = event["server"].get_user(nick)
        steam_id = user.get_setting("steamid", None)

        if not steam_id:
            event["stderr"].write(("%s does not have a steam account associated with their account" % nick))
            return False

    @utils.hook("received.command.steamstats", channel_only=True)
    @utils.kwarg("help", "Get users steam summary")
    @utils.spec("!<nick>lstring")
    def user_summary(self, event):
        nick = event["spec"][0]

        self._account_from_nick(event, nick)
