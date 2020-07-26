#--depends-on commands
#--depends-on config
#--depends-on permissions
#--require-config steam-api-key

import time, math, pprint
from steam import webapi, steamid
from steam.steamid import steam64_from_url, SteamID
from steam.webapi import WebAPI
from src import EventManager, ModuleManager, utils, IRCChannel, IRCServer, IRCBot
from src.core_modules import commands
from src.core_modules.commands import outs
from src.core_modules.commands.outs import StdOut
from . import consts

#TypeError: __init__() missing 6 required positional arguments: 'definition', 'bot', 'events', 'exports', 'timers', and 'log'
