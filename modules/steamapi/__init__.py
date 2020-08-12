#--depends-on commands
#--depends-on config
#--depends-on permissions
#--require-config steam-api-key

from steam.webapi import WebAPI

from src import ModuleManager, utils
from . import api, consts, formatter, user


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
    @utils.spec("?<nick>word ?<short>word")
    def user_summary(self, event):
        nick = event["spec"][0] if event["spec"][0] != None else event["user"].nickname
        short = event["spec"][1] == "short"

        steam_id = user.get_id_from_nick(event, nick, self.api)
        if steam_id == consts.NO_STEAMID:
            return consts.NO_STEAMID

        steam_id = steam_id.as_64

        summary = self.get_player_summary(steam_id)

        if summary["players"] == "":
            event["stderr"].write("Could not find that user")
            return consts.NO_STEAMID
        else:
            summary = summary["players"][0]

        status = consts.user_state(summary["personastate"])
        steam_name = summary["personaname"]
        display_name = steam_name if "realname" not in summary else summary["realname"]
        currently_playing = False if "gameextrainfo" not in summary else summary["gameextrainfo"]

        if short == True:
            message = formatter.short_user_summary(
                event,
                sname=steam_name,
                name=display_name,
                status=status,
                url=summary["profileurl"]
            )

            event["stdout"].write(message)
            return True

        visibility = formatter.visibility(event, summary["communityvisibilitystate"])
        owned_games = self.get_owned_games(steam_id)
        lastlogoff = "" if "lastlogoff" not in summary else summary["lastlogoff"]

        # If we have no games, fail silently
        game_count = owned_games["game_count"]

        if game_count < 1:
            return False

        total_playtime = self.get_total_playtime(owned_games["games"])
        top_game_time, top_game_name = self.get_top_game(steam_id, owned_games)

        last_seen = "" if (lastlogoff == "") else lastlogoff

        message = formatter.extended_user_summary(
            event,
            names={
                "steam": steam_name,
                "display": display_name
            },
            status=status,
            visibility=visibility,
            game_count=game_count,
            top_game={
                "name": top_game_name,
                "time": top_game_time
            },
            total_playtime=total_playtime,
            last_seen=last_seen,
            currently_playing=currently_playing,
            url=summary["profileurl"]
        )

        event["stdout"].write(message)
        return True

    @utils.hook("received.command.topgames", channel_only=True)
    @utils.kwarg("help", "Get users steam summary")
    @utils.spec("?<nick>word ?<amount>word")
    def top_games(self, event):
        nick = event["spec"][0] if event["spec"][0] != None else event["user"].nickname
        amount = event["spec"][1] if event["spec"][1] != None else 5
        amount = amount if str(event["spec"][1]).isdigit() == False else int(event["spec"][1])

        max_amount = 8
        amount = max_amount if amount > max_amount else amount

        steam_id = user.get_id_from_nick(event, nick, self.api)
        if steam_id == consts.NO_STEAMID:
            return consts.NO_STEAMID

        summary = self.get_owned_games(steam_id)
        gamelist = summary["games"]
        games = list()

        total_user_playtime = 0

        for game in gamelist:
            total_playtime = game["playtime_forever"] * 60
            total_user_playtime = total_user_playtime + total_playtime
            games.append([total_playtime, game["name"]])

        games.sort(reverse=True)
        games = games[0:amount]

        summary = self.get_player_summary(steam_id)
        summary = summary["players"][0]

        games_parsed = list()
        for game in games:
            pretty_time = utils.datetime.format.to_pretty_time(game[0], max_units=2)
            games_parsed.append([pretty_time, game[1]])

        lang = list()

        total_user_playtime_parsed = utils.datetime.format.to_pretty_time(total_user_playtime)

        i = 1
        for time, name in games_parsed:
            parsed = "%s. %s (%s)" % (
                utils.irc.bold(i),
                utils.irc.color(utils.irc.bold(name),
                                utils.consts.GREEN),
                time
            )
            lang.append(parsed)
            i = i + 1

        event["stdout"].write("%s's top %d games: %s" % (summary["personaname"], amount, "  —  ".join(lang)))

    @utils.hook("received.command.recentgames", channel_only=True)
    @utils.kwarg("help", "Get users recent game history")
    @utils.spec("?<nick>word")
    def game_summary(self, event):
        nick = event["spec"][0] if event["spec"][0] != None else event["user"].nickname

        steam_id = user.get_id_from_nick(event, nick, self.api)
        if steam_id == consts.NO_STEAMID:
            return consts.NO_STEAMID

        steam_id = steam_id.as_64

        summary = self.get_player_summary(steam_id)
        summary = summary["players"][0]
        steam_name = summary["personaname"]
        display_name = steam_name if "realname" not in summary else summary["realname"]

        page = self.get_recent_games(steam_id)
        total_count = page["total_count"]

        if total_count == 0:
            event["stderr"].write("No games played by %s in the last 2 weeks" % steam_name)
            return False

        recent_games = page["games"]
        print(page)
        fgames = list()
        for i in range(total_count):
            game = recent_games[i]

            appid = game["appid"]
            playtime = (game["playtime_2weeks"] * 60)
            playtime_parsed = utils.datetime.format.to_pretty_time(playtime)
            name = ("Unknown Game (ID: %d)" % appid) if "name" not in game else game["name"]

            fgames.append([playtime_parsed, name])

        lang = list()
        for time, name in fgames:
            parsed = "%s (%s)" % (utils.irc.color(utils.irc.bold(name), utils.consts.GREEN), time)
            lang.append(parsed)

        formatted_string = "%s %s" % (utils.irc.bold(display_name + "'s 2wk activity:"), "  —  ".join(lang))
        event["stdout"].write(formatted_string)

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

    def get_recent_games(self, id):
        api_key = self.api_key

        json = {
            "steamid": id,
            "key": api_key
        }

        page = self.get_service_worker("IPlayerService.GetRecentlyPlayedGames", json)
        return page


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
