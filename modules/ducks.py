# --depends-on commands
# --depends-on config

import random
import re
import time
from src import EventManager, ModuleManager, utils

DUCK_TAIL = "・゜゜・。。・゜゜"
DUCK = ["\\_o< ", "\\_O< ", "\\_0< ", "\\_\u00f6< ", "\\_\u00f8< ", "\\_\u00f3< "]
DUCK_NOISE = ["QUACK!", "FLAP FLAP!", "quack!", "squawk!", "HONK HONK HONK"]

DEFAULT_MIN_MESSAGES = 100


@utils.export(
    "channelset",
    utils.BoolSetting("ducks-enabled",
                      "Whether or not to spawn ducks"),
)
@utils.export(
    "channelset",
    utils.BoolSetting("ducks-missed-time",
                      "Whether or not to show how long in seconds you missed a duck by"),
)
@utils.export(
    "channelset",
    utils.IntRangeSetting(20,
                          200,
                          "ducks-min-messages",
                          "Minimum messages between ducks spawning"),
)
@utils.export(
    "channelset",
    utils.BoolSetting(
        "ducks-kick",
        "Whether or not to kick someone talking to non-existent ducks",
    ),
)
@utils.export(
    "channelset",
    utils.BoolSetting(
        "ducks-prevent-highlight",
        "Whether or not to prevent highlighting users with !friends/!enemies",
    ),
)
class Module(ModuleManager.BaseModule):

    _is_special = False

    @utils.hook("new.channel")
    def new_channel(self, event):
        self.bootstrap_channel(event["channel"])

    def bootstrap_channel(self, channel):
        if not hasattr(channel, "duck_active"):
            channel.duck_active = None
            channel.duck_lines = 0

    def _activity(self, channel):
        self.bootstrap_channel(channel)

        ducks_enabled = channel.get_setting("ducks-enabled", False)

        if ducks_enabled and not channel.duck_active and not channel.duck_lines == -1:
            channel.duck_lines += 1
            min_lines = channel.get_setting("ducks-min-messages", DEFAULT_MIN_MESSAGES)

            if channel.duck_lines >= min_lines:
                show_duck = random.SystemRandom().randint(1, 15) == 1
                if show_duck:
                    self._trigger_duck(channel)

    @utils.hook("command.regex")
    @utils.kwarg("expect_output", False)
    @utils.kwarg("ignore_action", False)
    @utils.kwarg("command", "duck-trigger")
    @utils.kwarg("pattern", re.compile(".+"))
    def channel_message(self, event):
        self._activity(event["target"])

    def _trigger_duck(self, channel):
        channel.duck_lines = -1
        delay = random.SystemRandom().randint(5, 20)
        self.timers.add("duck", self._send_duck, delay, channel=channel)

    def _send_duck(self, timer):
        channel = timer.kwargs["channel"]
        channel.duck_active = time.time()
        channel.duck_lines = 0

        build_duck = DUCK_TAIL + random.choice(DUCK) + utils.irc.bold(random.choice(DUCK_NOISE))

        self._is_special = (random.SystemRandom().randint(1, 20) == 7)

        if self._is_special == True:
            build_duck = utils.irc.color(build_duck, utils.consts.RED)

        channel.send_message(build_duck)

    def _duck_action(self, channel, user, action, setting):
        duck_timestamp = channel.duck_active
        channel.set_setting("duck-last", time.time())
        channel.duck_active = None

        seconds = round(time.time() - duck_timestamp, 2)

        user_id = user.get_id()
        action_count = channel.get_user_setting(user_id, setting, 0)
        action_count += 1
        channel.set_user_setting(user_id, setting, action_count)

        ducks_plural = "duck" if action_count == 1 else "ducks"
        duck_special = utils.irc.color(utils.irc.bold("rabid "), utils.consts.RED) if self._is_special else ""

        return "%s %s a %sduck in %s seconds! You've %s %s %s in %s!" % (
            utils.irc.bold(user.nickname),
            action,
            duck_special,
            utils.irc.bold(seconds),
            action,
            utils.irc.bold(action_count),
            ducks_plural,
            utils.irc.bold(channel.name),
        )

    def _no_duck(self, channel, user, stderr):
        message = "There was no duck!"
        duck_timestamp = channel.get_setting("duck-last", None)

        if not duck_timestamp == None and channel.get_setting("ducks-missed-time", False):
            seconds = round(time.time() - duck_timestamp, 2)
            message += " The last duck was %s seconds ago!" % utils.irc.bold(seconds)

        if channel.get_setting("ducks-kick"):
            channel.send_kick(user.nickname, message)
        else:
            stderr.write("%s: %s" % (user.nickname, message))

    @utils.hook("received.command.bef", alias_of="befriend")
    @utils.hook("received.command.befriend")
    @utils.kwarg("help", "Befriend a duck")
    @utils.spec("!-channelonly")
    def befriend(self, event):
        if event["target"].duck_active:
            action = self._duck_action(event["target"], event["user"], "befriended", "ducks-befriended")
            event["stdout"].write(action)
        else:
            self._no_duck(event["target"], event["user"], event["stderr"])

    @utils.hook("received.command.bang", alias_of="trap")
    @utils.hook("received.command.trap")
    @utils.kwarg("help", "Shoot a duck")
    @utils.spec("!-channelonly")
    def trap(self, event):
        if event["target"].duck_active:
            action = self._duck_action(event["target"], event["user"], "killed", "ducks-shot")
            event["stdout"].write(action)
        else:
            self._no_duck(event["target"], event["user"], event["stderr"])

    def _target(self, target, is_channel, query):
        if query:
            if not query == "*":
                return query
        elif is_channel:
            return target.name

    @utils.hook("received.command.friends")
    @utils.kwarg("help", "Show top 10 duck friends")
    @utils.spec("?<channel>word")
    def friends(self, event):
        query = self._target(event["target"], event["is_channel"], event["spec"][0])

        stats = self._top_duck_stats(
            event["server"],
            event["target"],
            "ducks-befriended",
            "friends",
            query,
        )
        event["stdout"].write(stats)

    @utils.hook("received.command.enemies")
    @utils.kwarg("help", "Show top 10 duck enemies")
    @utils.spec("?<channel>word")
    def enemies(self, event):
        query = self._target(event["target"], event["is_channel"], event["spec"][0])

        stats = self._top_duck_stats(event["server"], event["target"], "ducks-shot", "enemies", query)
        event["stdout"].write(stats)

    def _top_duck_stats(self, server, target, setting, description, channel_query):
        channel_query_str = ""
        if not channel_query == None:
            channel_query = server.irc_lower(channel_query)
            channel_query_str = " in %s" % utils.irc.bold(channel_query)

        stats = server.find_all_user_channel_settings(setting)

        user_stats = {}
        for channel, nickname, value in stats:
            if not channel_query or channel_query == channel:
                if not nickname in user_stats:
                    user_stats[nickname] = 0
                user_stats[nickname] += value

        top_10 = utils.top_10(
            user_stats,
            convert_key=lambda n: utils.irc.bold(self._get_nickname(server,
                                                                    target,
                                                                    n)),
        )
        return "Top duck %s%s: %s" % (
            description,
            channel_query_str,
            ", ".join(top_10),
        )

    def _get_nickname(self, server, target, nickname):
        nickname = server.get_user(nickname).nickname
        if target.get_setting("ducks-prevent-highlight", True):
            nickname = utils.prevent_highlight(nickname)
        return nickname

    @utils.hook("received.command.duckstats")
    @utils.kwarg("help", "Get yours, or someone else's, duck stats")
    @utils.spec("?<nickname>ouser")
    def duckstats(self, event):
        target_user = event["spec"][0] or event["user"]

        befs = target_user.get_channel_settings_per_setting("ducks-befriended")
        traps = target_user.get_channel_settings_per_setting("ducks-shot")

        all = [(chan, val, "bef") for chan, val in befs]
        all += [(chan, val, "trap") for chan, val in traps]

        current = {
            "bef": 0,
            "trap": 0
        }
        overall = {
            "bef": 0,
            "trap": 0
        }

        if event["is_channel"]:
            for channel_name, value, action in all:
                if not action in overall:
                    overall[action] = 0
                overall[action] += value

                if event["is_channel"]:
                    channel_name_lower = event["server"].irc_lower(channel_name)
                    if channel_name_lower == event["target"].name:
                        current[action] = value

        current_str = ""
        if current:
            current_str = " (%s Befriended, %s Killed in %s)" % (
                utils.irc.bold(current["bef"]),
                utils.irc.bold(current["trap"]),
                utils.irc.bold(event["target"].name),
            )

        event["stdout"].write("%s has befriended %s and killed %s ducks%s" % (
            utils.irc.bold(target_user.nickname),
            utils.irc.bold(overall["bef"]),
            utils.irc.bold(overall["trap"]),
            current_str,
        ))

    @utils.hook("received.command.setduckfriends")
    @utils.kwarg("permission", "setducks")
    @utils.kwarg("min_args", 2)
    @utils.kwarg("channel_only", True)
    def setduckfriends(self, event):

        target_user = event["server"].get_user(event["args_split"][0])
        amount = int(event["args_split"][1])

        user_id = target_user.get_id()
        event["target"].set_user_setting(user_id, "ducks-befriended", amount)

        event["stdout"].write("Set %s's befriended ducks to %d" % (target_user, amount))

    @utils.hook("received.command.setduckenemies")
    @utils.kwarg("permission", "setducks")
    @utils.kwarg("min_args", 2)
    @utils.spec("!-channelonly")
    def setduckenemies(self, event):

        target_user = event["server"].get_user(event["args_split"][0])
        amount = int(event["args_split"][1])

        user_id = target_user.get_id()
        event["target"].set_user_setting(user_id, "ducks-shot", amount)

        event["stdout"].write("Set %s's killed ducks to %d" % (target_user, amount))

    @utils.hook("received.command.resetuserducks")
    @utils.kwarg("permission", "setducks")
    @utils.kwarg("min_args", 1)
    @utils.spec("!-channelonly")
    def resetuserducks(self, event):

        target_user = event["server"].get_user(event["args_split"][0])

        user_id = target_user.get_id()
        event["target"].set_user_setting(user_id, "ducks-shot", 0)
        event["target"].set_user_setting(user_id, "ducks-befriended", 0)

        event["stdout"].write("Reset %s's ducks to 0." % (target_user))
