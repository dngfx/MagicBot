#--depends-on commands
#--depends-on config
#--depends-on permissions
#--require-config steam-api-key

import time, math, pprint
from steam import webapi, steamid
from steam.steamid import steam64_from_url, SteamID
from steam.webapi import WebAPI
from src import EventManager, ModuleManager, utils, IRCChannel

API = {
    "personastate":
        {
            0: "Offline",
            1: "Online",
            2: "Busy",
            3: "Away",
            4: "Snooze",
            5: "Looking to trade",
            6: "Looking to play"
        }
}


@utils.export("set", utils.Setting("steamid", "Set your steam id", example="103582791429521412"))
class Module(ModuleManager.BaseModule):

    def on_load(self):
        api_key = self.bot.config["steam-api-key"]
        self._api = WebAPI(api_key, format="json", raw=False)

    def api(self) -> WebAPI:
        return self._api

    def _steam_id(self, event, id):
        sid = SteamID(id)
        if not self._is_valid(sid):
            # Try Resolving a vanity url
            sid = self._get_id_from_url(id)
            if sid == False:
                event["syserr"].write("Could not resolve steam id")
                return False

            sid = SteamID(sid)
            if not self._is_valid(sid):
                event["syserr"].write("Could not resolve steam id")
                return False

        return sid

    def _get_id_from_url(self, url):
        id = self.api().call('ISteamUser.ResolveVanityURL', vanityurl=url)["response"]

        if id["success"] != 1:
            return False

        return id["steamid"]

    def _is_valid(self, id: SteamID):
        return id.is_valid()

    def _set_steamid(self, event, nick, steamid):
        user = event["server"].get_user(nick)
        user.set_setting("steamid", steamid)

    def _account_from_nick(self, event, nick):
        if not event["server"].has_user_id(nick):
            return False

        user = event["server"].get_user(nick)
        steam_id = user.get_setting("steamid", None)

        if not steam_id:
            event["stderr"].write(("%s does not have a steam account associated with their account" % nick))
            return False

        return self._steam_id(event, steam_id)

    def _get_player_summary(self, id):
        return self.api().call("ISteamUser.GetPlayerSummaries", steamids=id)["response"]["players"][0]

    @utils.hook("received.command.steamstats", channel_only=True)
    @utils.kwarg("help", "Get users steam summary")
    @utils.spec("?<nick>string")
    def user_summary(self, event):
        user = event["user"]
        nick = user.nickname if event["spec"][0] == None else event["spec"][0]

        steam_id = self._account_from_nick(event, nick)
        self._set_steamid(event, nick, steam_id)

        summary = self._get_player_summary(steam_id)
        print(summary)

        status = API["personastate"][summary["personastate"]]
        steam_name = summary["personaname"]

        message = "User Summary (%s): Status: %s" % (utils.irc.bold(steam_name), utils.irc.bold(status))

        event["stdout"].write(message)


    """ 
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
        'gameextrainfo':
            'Fall Guys: Technical Beta',
        'gameid':
            '1265940',
        'loccountrycode':
            'MX'
    } """
