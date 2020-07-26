#--depends-on commands
#--depends-on config
#--depends-on permissions
#--require-config steam-api-key

import time, math, pprint
from steam import webapi, steamid
from steam.steamid import steam64_from_url, SteamID
from steam.webapi import WebAPI
from src import EventManager, ModuleManager, utils, IRCChannel
from . import consts as SteamConsts
from . import api as SteamAPI
from . import user as SteamUser

_bot = None
_events = None
_exports = None
_log = None


@utils.export("set", utils.Setting("steamid", "Set your steam id", example="103582791429521412"))
class Module(ModuleManager.BaseModule):
    _name = "Steam"
    api_loaded = False

    stdout = None
    stderr = None

    def connect(self):
        api_key = self.bot.config["steam-api-key"]
        self.api = WebAPI(api_key, format="json")

    def get_api(self) -> WebAPI:
        if not self.api_loaded:
            self.connect()

        return self.api

    def on_load(self):
        self.connect()

    def call(self, method, **kwargs):
        call = self.get_api().call(method, **kwargs)
        return call["response"]

    @utils.hook("received.command.steamstats", channel_only=True)
    @utils.kwarg("help", "Get users steam summary")
    @utils.spec("?<nick>string")
    def user_summary(self, event):
        user = event["user"]
        nick = user.nickname if event["spec"][0] == None else event["spec"][0]
        steam_id = SteamUser.get_id_from_nick(event, nick)

        SteamUser.set_user(event["server"], nick, steam_id)

        summary = self.get_player_summary(steam_id)

        if not summary["players"]:
            event["stderr"].write("Could not find that user")
            return

        summary = summary["players"][0]

        status = SteamConsts.user_state(summary["personastate"])
        steam_name = summary["personaname"]

        message = "User Summary (%s): Status: %s" % (utils.irc.bold(steam_name), utils.irc.bold(status))

        event["stdout"].write(message)

    def get_player_summary(self, id):
        return self.call("ISteamUser.GetPlayerSummaries", steamids=id)

    """ {
        'players':
            [
                {
                    'steamid':
                        '76561198028248833',
                    'communityvisibilitystate':
                        3,
                    'profilestate':
                        1,
                    'personaname':
                        'erica',
                    'profileurl':
                        'https://steamcommunity.com/id/ericathesnark/',
                    'avatar':
                        'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/5f/5f8655f3e24f3c1a27b2e38ffd2c968d8f28a594.jpg',
                    'avatarmedium':
                        'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/5f/5f8655f3e24f3c1a27b2e38ffd2c968d8f28a594_medium.jpg',
                    'avatarfull':
                        'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/5f/5f8655f3e24f3c1a27b2e38ffd2c968d8f28a594_full.jpg',
                    'avatarhash':
                        '5f8655f3e24f3c1a27b2e38ffd2c968d8f28a594',
                    'lastlogoff':
                        1595735237,
                    'personastate':
                        1,
                    'realname':
                        'Erica',
                    'primaryclanid':
                        '103582791464854615',
                    'timecreated':
                        1280276956,
                    'personastateflags':
                        0,
                    'loccountrycode':
                        'MX'
                }
            ]
    } """
