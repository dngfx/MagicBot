#--depends-on commands
#--depends-on config
#--depends-on permissions
#--require-config steam-api-key

import time, math, pprint, datetime, pprint, urllib.parse, operator
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

SERVICEWORKER_URL = "https://api.steampowered.com/%s/%s/v%s/"


@utils.export(
    "set",
    utils.Setting("steamid",
                  "Set your steam id",
                  example="1234567, https://steamcommunity.com/id/user")
)
class Module(ModuleManager.BaseModule):
    _name = "Steam"
    api_loaded = False

    stdout = None
    stderr = None

    def connect(self):
        self.api_key = self.bot.config["steam-api-key"]
        self.api = WebAPI(self.api_key, format="json")

    def get_api(self) -> WebAPI:
        if not self.api_loaded:
            self.connect()

        return self.api

    def on_load(self):
        self.connect()

    def call(self, method, **kwargs):
        call = self.get_api().call(method, **kwargs)
        return call["response"]

    def get_service_worker(self, method, json, version="0001"):
        interface, method = method.split(".")

        page = utils.http.request(SERVICEWORKER_URL % (interface, method, version), get_params=json).json()

        return page["response"]

    @utils.hook("received.command.steamstats", channel_only=True)
    @utils.kwarg("help", "Get users steam summary")
    @utils.spec("?<nick>string")
    def user_summary(self, event):
        spec = event["spec"][0]
        nick = event["user"].nickname

        if spec is not None:
            nick = spec

        steam_id = SteamUser.get_id_from_nick(event, nick, self.api)
        if steam_id == SteamConsts.NO_STEAMID:
            return SteamConsts.NO_STEAMID

        summary = self.get_player_summary(steam_id)

        if summary["players"] == "":
            event["stderr"].write("Could not find that user")
            return SteamConsts.NO_STEAMID

        summary = summary["players"][0]

        status = SteamConsts.user_state(summary["personastate"])
        steam_name = summary["personaname"]

        visibility = summary["communityvisibilitystate"]
        if visibility == 1:
            visibility = "Private"
        elif visibility == 3:
            visibility = "Public"
        else:
            visibility = "Unknown"

        last_seen = ""

        display_name = steam_name if "realname" not in summary else summary["realname"]

        total_games_list = self.get_owned_games(steam_id.as_64)
        game_count = total_games_list["game_count"]

        total_games = ""
        top_game = ""
        total_time_played = ""

        if game_count > 0:
            total_games = " — Games Owned: %s" % utils.irc.bold(game_count)
            total_time_played = self.get_total_playtime(total_games_list["games"])
            top_game_time, top_game_name = self.get_top_game(steam_id.as_64, total_games_list)
            top_game = (
                " — Top Game: %s with %s played" % (utils.irc.bold(top_game_name),
                                                    utils.irc.bold(top_game_time))
            )

            total_time_played = " — Total Time Played: %s" % utils.irc.bold(total_time_played)

        if "lastlogoff" in summary:
            pretty_time = utils.datetime.format.to_pretty_time(
                (datetime.datetime.now() - datetime.datetime.fromtimestamp(summary["lastlogoff"])).total_seconds()
            )

            last_seen = " — Last Seen: %s ago" % utils.irc.bold(pretty_time)

        currently_playing = ""

        if "gameextrainfo" in summary:
            currently_playing = " — Currently Playing: %s" % utils.irc.bold(summary["gameextrainfo"])

        message = "Summary for %s (%s): Status: %s — Visibility: %s%s%s%s%s%s — Profile: %s" % (
            steam_name,
            utils.irc.bold(display_name),
            utils.irc.bold(status),
            utils.irc.bold(visibility),
            total_games,
            top_game,
            total_time_played,
            last_seen,
            currently_playing,
            utils.irc.bold(summary["profileurl"])
        )

        event["stdout"].write(message)

    @utils.hook("received.command.topgames", channel_only=True)
    @utils.kwarg("help", "Get users steam summary")
    @utils.spec("?<nick>string")
    def game_summary(self, event):
        user = event["user"]
        nick = user.nickname if event["spec"][0] == None else event["spec"][0]
        steam_id = SteamUser.get_id_from_nick(event, nick, self.api)
        if steam_id == SteamConsts.NO_STEAMID:
            return SteamConsts.NO_STEAMID

        summary = self.get_owned_games(steam_id)
        gamelist = summary["games"]
        games = list()

        total_user_playtime = 0

        for game in gamelist:
            total_playtime = game["playtime_forever"] * 60
            total_user_playtime = total_user_playtime + total_playtime
            games.append([total_playtime, game["name"]])

        games.sort(reverse=True)
        games = games[0:5]

        summary = self.get_player_summary(steam_id)
        summary = summary["players"][0]

        games_parsed = list()
        for game in games:
            pretty_time = utils.datetime.format.to_pretty_time(game[0])
            games_parsed.append([pretty_time, game[1]])

        lang = list()

        total_user_playtime_parsed = utils.datetime.format.to_pretty_time(total_user_playtime)

        i = 1
        for time, name in games_parsed:
            parsed = "#%s) %s — Played: %s" % (utils.irc.bold(i), utils.irc.bold(name), utils.irc.bold(time))
            lang.append(parsed)
            i = i + 1

        event["stdout"].write("Top 5 Games for %s: %s" % (summary["personaname"], " — ".join(lang)))

    def get_owned_games(self, id):
        api_key = self.api_key

        json = {
            "steamid": id,
            "include_appinfo": True,
            "include_played_free_games": True,
            "key": api_key
        }

        page = self.get_service_worker("IPlayerService.GetOwnedGames", json)
        return page

    def get_total_playtime(self, gamelist):
        total = 0
        for game in gamelist:
            total = total + (game["playtime_forever"] * 60)

        total = utils.datetime.format.to_pretty_time(total)

        return total

    def get_top_game(self, id, games_list=None):
        gamelist = games_list if games_list != None else self.get_owned_games(id)

        if "games" in gamelist:
            gamelist = gamelist["games"]

        games = list()

        for game in gamelist:
            games.append([game["playtime_forever"], game["name"]])

        games.sort(reverse=True)
        games = games[0]

        pretty_time = utils.datetime.format.to_pretty_time(games[0])

        return [pretty_time, games[1]]

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
