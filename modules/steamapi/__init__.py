#--depends-on commands
#--depends-on config
#--depends-on permissions
#--require-config steam-api-key

import time, math, pprint, datetime
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

        print(summary)

        if not summary["players"]:
            event["stderr"].write("Could not find that user")
            return

        summary = summary["players"][0]

        status = SteamConsts.user_state(summary["personastate"])
        steam_name = summary["personaname"]

        visibility = summary["communityvisibilitystate"]
        if visibility == 1:
            visibility = "Private"
        elif visibility == 3:
            visibility = "Public"

        last_seen = ""

        display_name = summary["realname"] if "realname" in summary else steam_name

        if "lastlogoff" in summary:
            pretty_time = utils.datetime.format.to_pretty_time(
                (datetime.datetime.now() - datetime.datetime.fromtimestamp(summary["lastlogoff"])).total_seconds()
            )
            last_seen = " — Last Seen: %s ago" % utils.irc.bold(pretty_time)

        currently_playing = ""

        if "gameextrainfo" in summary:
            currently_playing = " — Currently Playing: %s" % utils.irc.bold(summary["gameextrainfo"])

        message = "%s (%s): Status: %s — Visibility: %s%s%s — Profile: %s" % (
            steam_name,
            utils.irc.bold(display_name),
            utils.irc.bold(status),
            utils.irc.bold(visibility),
            last_seen,
            currently_playing,
            utils.irc.bold(summary["profileurl"])
        )

        event["stdout"].write(message)

    def get_player_summary(self, id):
        return self.call("ISteamUser.GetPlayerSummaries", steamids=id)


""" {
    'players':
        [
            {
                'steamid':
                    '76561198002971551',
                'communityvisibilitystate':
                    3,
                'profilestate':
                    1,
                'personaname':
                    'dongfix',
                'commentpermission':
                    1,
                'profileurl':
                    'https://steamcommunity.com/id/dngfx/',
                'avatar':
                    'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/88/88a1f6a28c60d6067b7b2f129a771660d0a68be3.jpg',
                'avatarmedium':
                    'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/88/88a1f6a28c60d6067b7b2f129a771660d0a68be3_medium.jpg',
                'avatarfull':
                    'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/88/88a1f6a28c60d6067b7b2f129a771660d0a68be3_full.jpg',
                'avatarhash':
                    '88a1f6a28c60d6067b7b2f129a771660d0a68be3',
                'personastate':
                    3,
                'realname':
                    'Dan',
                'primaryclanid':
                    '103582791429521408',
                'timecreated':
                    1227153609,
                'personastateflags':
                    0,
                'loccountrycode':
                    'GB',
                'locstatecode':
                    'C3',
                'loccityid':
                    16614
            }
        ]
} """
