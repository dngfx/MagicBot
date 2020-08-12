#--depends-on commands
#--depends-on config
#--depends-on permissions
#--require-config steam-api-key

import re

from steam.steamid import steam64_from_url, SteamID

from . import consts


"""
https://steamcommunity.com/gid/[g:1:4]
https://steamcommunity.com/gid/103582791429521412
https://steamcommunity.com/groups/Valve
https://steamcommunity.com/profiles/[U:1:12]
https://steamcommunity.com/profiles/76561197960265740
https://steamcommunity.com/id/johnc
https://steamcommunity.com/user/cv-dgb/
"""

PROFILE_REGEX = re.compile("https?://(?:www\.)?steamcommunity.com/\w+/([^/]+)", re.I)


# Logic to figure out where the steam id is
def get_id(event, id, nick):
    parsed_id = SteamID(id)

    # If the steamid passed isn't valid, see if it's a vanity url
    if not is_valid(parsed_id):
        parsed_id_url = get_id_from_url(id)

        if parsed_id_url == False:
            event["stderr"].write("Could not resolve Steam ID")
            return consts.NO_STEAMID

        parsed_id = SteamID(parsed_id_url)

        if not is_valid(parsed_id):
            event["stderr"].write("Could not resolve Steam ID")
            return consts.NO_STEAMID

    # return the valid id
    return parsed_id


def set_user(server, nick, steam_id):
    user = server.get_user(nick)
    user.set_setting("steamid", steam_id)


def is_valid(id: SteamID):
    return id.is_valid()


def get_id_from_url(url, api):
    url_match = PROFILE_REGEX.match(url)
    if url_match != None:
        steam_id = steam64_from_url(url=url)

        return SteamID(steam_id)

    steam_id = api.call("ISteamUser.ResolveVanityURL", vanityurl=url, url_type=1)["response"]

    if steam_id["success"] == 42:
        return consts.NO_STEAMID

    return steam_id["steamid"]


def get_id_from_nick(event, nick, api):
    server = event["server"]
    has_user = server.has_user_id(nick)

    if has_user == False:
        event["stderr"].write("Nick not found on server")
        return consts.NO_STEAMID

    user = server.get_user(nick)
    steam_id = user.get_setting("steamid", None)

    if steam_id == None:
        event["stderr"].write(("%s does not have a steam account associated with their account" % nick))
        return consts.NO_STEAMID

    check = str(steam_id)
    if check.isdigit() == False:
        steam_id = get_id_from_url(check, api)
        if steam_id == consts.NO_STEAMID:
            return consts.NO_STEAMID

    set_user(event["server"], nick, steam_id)

    return get_id(event, steam_id, nick)
