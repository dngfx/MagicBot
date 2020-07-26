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


# Logic to figure out where the steam id is
def get_id(event, id):
    parsed_id = SteamID(id)

    # If the steamid passed isn't valid, see if it's a vanity url
    if not is_valid(parsed_id):
        parsed_id_url = get_id_from_url(id)

        if parsed_id_url == False:
            event["stderr"].write("Could not resolve Steam ID")
            return false

        parsed_id = SteamID(parsed_id_url)

        if not is_valid(parsed_id):
            event["stderr"].write("Could not resolve Steam ID")
            return false

    # return the valid id
    return parsed_id


def set_user(server, nick, steam_id):
    user = server.get_user(nick)
    user.set_setting("steamid", steam_id)


def is_valid(id: SteamID):
    return id.is_valid()


def get_id_from_url(url):
    steam_id = SteamAPI.call("ISteamUser.ResolveVanityURL", vanityurl=url)
    if steam_id["success"] != 1:
        return False

    return steam_id["steamid"]


def get_id_from_nick(event, nick):
    server = event["server"]
    if not server.has_user_id(nick):
        event["stderr"].write("Nick not found on server")
        return False

    user = server.get_user(nick)
    steam_id = user.get_setting("steamid", None)

    if not steam_id:
        event["stderr"].write(("%s does not have a steam account associated with their account" % nick))
        return False

    set_user(event["server"], nick, steam_id)

    return get_id(event, steam_id)
