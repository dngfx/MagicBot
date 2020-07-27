#--depends-on commands
#--depends-on config
#--depends-on permissions
#--require-config steam-api-key

import time, math, pprint, datetime, pprint, urllib.parse, operator
from steam import webapi, steamid
from steam.steamid import steam64_from_url, SteamID
from steam.webapi import WebAPI
from src import EventManager, ModuleManager, utils, IRCChannel
from . import consts, api, user

FORMATTED_MESSAGES = {
    "short_user_summary": "Shortened summary for %s (%s): Status: %s — Profile: %s"
}


def bold(text):
    return utils.irc.bold(text)


def short_user_summary(event, **kwargs):
    fmt = kwargs

    steam_name = fmt["sname"]
    display_name = fmt["name"]
    status = fmt["status"]
    profile_url = fmt["url"]

    message = "Shortened summary for %s (%s): Status: %s — Profile: %s" % (
        steam_name,
        utils.irc.bold(display_name),
        utils.irc.bold(status),
        utils.irc.bold(profile_url)
    )

    return message


def extended_user_summary(event, **kwargs):
    fmt = kwargs

    names = fmt["names"]
    steam_name = names["steam"]
    display_name = names["display"]
    status_kwarg = fmt["status"]
    status = ("Status: %s" % bold(status_kwarg))
    visibility_kwarg = fmt["visibility"]
    visibility = ("Visibility: %s" % bold(visibility_kwarg))
    game_count_kwarg = fmt["game_count"]
    game_count = ("Games Owned: %d" % game_count_kwarg)
    top_game_args = fmt["top_game"]
    top_game = ("Top Game: %s with %s played" % (bold(top_game_args["name"]), bold(top_game_args["time"])))
    total_playtime_kwarg = fmt["total_playtime"]
    total_playtime = ("Total Played: %s" % bold(total_playtime_kwarg))
    last_seen = fmt["last_seen"]
    currently_playing = fmt["currently_playing"]

    if last_seen != "":
        formatted_time = utils.datetime.format.to_pretty_time(
            (datetime.datetime.now() - datetime.datetime.fromtimestamp(last_seen)).total_seconds()
        )
        print(formatted_time)

        last_seen = " — Last Seen: %s ago" % bold(formatted_time)

    playing = ""
    if currently_playing != False:
        playing = " — Currently Playing: %s" % bold(currently_playing)

    profile_url = fmt["url"]
    message = "Summary for %s (%s): %s — %s — %s — %s — %s%s%s — %s" % (
        steam_name,
        display_name,
        status,
        visibility,
        game_count,
        top_game,
        total_playtime,
        last_seen,
        playing,
        profile_url
    )

    return message


def visibility(event, visibility):
    if visibility == 1:
        visibility = "Private"
    elif visibility == 3:
        visibility = "Public"
    else:
        visibility = "Unknown"

    return visibility
