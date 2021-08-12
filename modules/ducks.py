# --depends-on commands
# --depends-on config

import random
import re
import time
import math

from src import ModuleManager, utils

""" Licence: WTFPL """

DUCK_TAIL = "・゜゜・。。・゜゜"
DUCK = ["\\_o< ", "\\_O< ", "\\_0< ",
        "\\_\u00f6< ", "\\_\u00f8< ", "\\_\u00f3< "]
DUCK_NOISE = ["QUACK!", "FLAP FLAP!", "quack!", "squawk!", "HONK HONK HONK"]

DUCK_GOLD_COLOR = utils.consts.GOLD
DUCK_RED_COLOR = utils.consts.RED
DUCK_METAL_COLOR = utils.consts.GREY

COLORS = [
    utils.consts.BLUE,
    utils.consts.LIGHTBLUE,
    utils.consts.CYAN,
    utils.consts.LIGHTCYAN,
    utils.consts.GREEN,
    utils.consts.LIGHTGREEN,
    utils.consts.YELLOW,
    utils.consts.ORANGE,
    utils.consts.BROWN,
    utils.consts.RED,
    utils.consts.PINK,
    utils.consts.PURPLE,
]

SPECIAL_DUCKS = [
    [{"type": "Gold", "color": DUCK_GOLD_COLOR, "lang": "Golden", "xpbonus": 5}],
    [{"type": "Metal", "color": DUCK_METAL_COLOR, "lang": "Metal", "xpbonus": 2}],
    [{"type": "Red", "color": DUCK_RED_COLOR, "lang": "Rabid", "xpbonus": 0.5}],
    [{"type": "Rainbow", "color": COLORS, "lang": "Mythical", "xpbonus": 10}],
]

DEFAULT_MIN_MESSAGES = 40
DEFAULT_MISS_COOLDOWN = 5
DEFAULT_MISS_CHANCE = 33  # Miss chance in %
# How many % the miss chance goes down when you miss
DEFAULT_MISS_CHANCE_REDUCTION = 2
DEFAULT_SPAWN_CHANCE = (
    2  # Chance a duck will spawn when the minimum number of messages have been reached
)
DEFAULT_SPECIAL_CHANCE = 2  # Special chance in %
DEFAULT_SPECIAL_ENABLED = False


@utils.export(
    "channelset", utils.BoolSetting(
        "ducks-enabled", "Whether or not to spawn ducks")
)
@utils.export(
    "channelset",
    utils.BoolSetting(
        "announce-xp-after-ducks",
        "Whether or not to announce total XP gain after ducks",
    ),
)
@utils.export(
    "channelset",
    utils.BoolSetting(
        "ducks-print-missed-time",
        "Whether or not to show how long in seconds you missed a duck by",
    ),
)
@utils.export(
    "channelset",
    utils.IntRangeSetting(
        10,
        200,
        "ducks-min-messages",
        "Minimum messages between ducks spawning (Min 10, max 200, default 40)",
    ),
)
@utils.export(
    "channelset",
    utils.IntRangeSetting(
        2,
        20,
        "ducks-spawn-chance",
        "Minimum messages between ducks spawning (Min 2, max 20, default 2)",
    ),
)
@utils.export(
    "channelset",
    utils.IntRangeSetting(
        2,
        10,
        "ducks-miss-cooldown",
        "Minimum time in seconds between being able to go for a duck again (Min 2, max 10, default 5)",
    ),
)
@utils.export(
    "channelset",
    utils.IntRangeSetting(0, 50, "ducks-miss-chance",
                          "Miss chance in % (Default 33%)"),
)
@utils.export(
    "channelset",
    utils.IntRangeSetting(
        2,
        5,
        "ducks-miss-chance-reduction",
        "Reduces chance to miss by this amount if you miss a duck (Default 2%)",
    ),
)
@utils.export(
    "channelset",
    utils.BoolSetting(
        "ducks-kick",
        "Whether or not to kick someone attempting to catch/kill a non-existent duck",
    ),
)
@utils.export(
    "channelset",
    utils.BoolSetting(
        "ducks-prevent-user-highlight",
        "Whether or not to prevent highlighting users with !friends/!enemies (Default True)",
    ),
)
@utils.export(
    "channelset",
    utils.BoolSetting(
        "ducks-enable-special",
        "Whether or not to allow spawning special (Golden / Metal / Rabid) ducks",
    ),
)
@utils.export(
    "channelset",
    utils.IntSetting(
        "ducks-special-chance",
        "Chance in percent a spawned duck will be special",
        example="2",
    ),
)
class Module(ModuleManager.BaseModule):
    @utils.hook("new.channel")
    def new_channel(self, event):
        self.bootstrap_channel(event["channel"], event["server"])

        return True

    def bootstrap_channel(self, channel, server):
        testing_enabled = server.get_setting("testing-enabled", False)
        testing_channel = server.get_setting("testing-channel", "NO_CHANNEL")

        if not hasattr(channel, "duck_active"):
            channel.duck_active = None
            channel.duck_lines = 0
            channel.duck_is_special = False
            channel.duck_special_type = 0
            channel.duck_cooldowns = {}
            channel._ducks_debug = testing_enabled
            channel._testing_channel = testing_channel
        else:
            channel._ducks_debug = testing_enabled
            channel._testing_channel = testing_channel

    def _activity(self, channel, server, event):
        self.bootstrap_channel(channel, event["server"])

        ducks_enabled = channel.get_setting("ducks-enabled", False)

        if ducks_enabled and not channel.duck_active and not channel.duck_lines == -1:
            channel.duck_lines += 1
            min_lines = channel.get_setting(
                "ducks-min-messages", DEFAULT_MIN_MESSAGES)

            if (
                channel._ducks_debug == True
                and channel.name != channel._testing_channel
            ):
                return False

            if channel._ducks_debug == True:
                min_lines = 1

            if channel.duck_lines >= min_lines:
                duck_chance = channel.get_setting(
                    "ducks-spawn-chance", DEFAULT_SPAWN_CHANCE
                )

                if channel._ducks_debug == True:
                    duck_chance = 100

                if random.randint(0, 99) < duck_chance:
                    self._trigger_duck(channel)

    @utils.hook("command.regex")
    @utils.kwarg("expect_output", False)
    @utils.kwarg("ignore_action", False)
    @utils.kwarg("command", "duck-trigger")
    @utils.kwarg("pattern", re.compile(".+"))
    def channel_message(self, event):
        self._activity(event["target"], event["server"], event)

    def _trigger_duck(self, channel):
        channel.duck_lines = -1
        delay = random.randint(5, 20)
        if channel._ducks_debug == True:
            delay = 1  # DEBUG
        self.timers.add("duck", self._send_duck, delay, channel=channel)

    def _build_duck(self, channel):
        duck = (
            DUCK_TAIL + random.choice(DUCK) +
            utils.irc.bold(random.choice(DUCK_NOISE))
        )
        duck_special_enabled = channel.get_setting(
            "ducks-enable-special", DEFAULT_SPECIAL_ENABLED
        )
        duck_special_chance = channel.get_setting(
            "ducks-special-chance", DEFAULT_SPECIAL_CHANCE
        )

        if channel._ducks_debug == True:
            duck_special_enabled = True
            duck_special_chance = 100

        if not duck_special_enabled:
            return duck

        if random.randint(0, 99) > duck_special_chance:
            return duck

        random_duck_type = random.randint(0, 2)

        rainbow_duck_chance = 5

        if channel._ducks_debug == True:
            rainbow_duck_chance = 33

        # 5% chance to generate a rainbow duck
        if random.randint(0, 99) < rainbow_duck_chance:
            random_duck_type = 3
            channel.duck_is_special = True
            channel.duck_special_type = random_duck_type
            duck = self._generate_rainbow_duck(duck)
            return duck

        random_duck_info = SPECIAL_DUCKS[random_duck_type][0]
        # 0 = gold, 1 = metal, 2 = red

        duck = utils.irc.color(duck, random_duck_info["color"])
        duck = utils.irc.bold(duck)
        channel.duck_is_special = True
        channel.duck_special_type = random_duck_type

        return duck

    def _generate_rainbow_duck(self, duck):
        args = utils.irc.strip_font(duck)

        offset = random.randint(0, len(COLORS))
        out = ""
        for i, c in enumerate(args):
            color = COLORS[(i + offset) % len(COLORS)]
            out += utils.irc.color(c, color, terminate=False)
        return utils.irc.bold(out)

    def _send_duck(self, timer):
        channel = timer.kwargs["channel"]
        channel.duck_active = time.time()
        channel.duck_lines = 0

        build_duck = self._build_duck(channel)
        channel.send_message(build_duck)

    # channel.duck_cooldowns =  {"dfx": { "cooldown_time": time, "missed_times": 0 }}
    def _has_shot_duck(self, event, channel, user, action):
        duck_miss_chance = channel.get_setting(
            "ducks-miss-chance", DEFAULT_MISS_CHANCE)
        duck_miss_reduction = channel.get_setting(
            "ducks-miss-chance-reduction", DEFAULT_MISS_CHANCE_REDUCTION
        )
        ducks_miss_cooldown = channel.get_setting(
            "ducks-miss-cooldown", DEFAULT_MISS_COOLDOWN
        )

        user_id = user.get_id()
        friend_count = channel.get_user_setting(user_id, "ducks-befriened", 0)
        enemy_count = channel.get_user_setting(user_id, "ducks-shot", 0)

        accuracy = math.ceil(66 * (friend_count + enemy_count) / 100)
        duck_miss_chance = duck_miss_chance - accuracy

        missed = False
        timenow = time.time()
        nick = user.nickname
        action = "shoot" if action == "killed" else "befriend"

        if nick not in channel.duck_cooldowns:
            channel.duck_cooldowns[nick] = {
                "cooldown_time": 0, "missed_times": 0}

        ustats = channel.duck_cooldowns[nick]

        duck_miss_chance = duck_miss_chance - (
            ustats["missed_times"] * duck_miss_reduction
        )

        # Are we shooting too fast?
        if timenow - ustats["cooldown_time"] < ducks_miss_cooldown:
            err = "You're exhausted and fail to %s the duck, try again soon" % action
            event["stderr"].write(err)
            return False

        # Are we going to miss?
        if random.randint(0, 99) < duck_miss_chance:
            missed = True

            channel.duck_cooldowns[nick]["cooldown_time"] = time.time()
            channel.duck_cooldowns[nick]["missed_times"] = ustats["missed_times"] + 1

            err = "Whoops! You fail to %s the duck, try again in %s seconds!" % (
                action,
                ducks_miss_cooldown,
            )

            event["stderr"].write(err)
            return False

        channel.duck_cooldowns[nick] = {"cooldown_time": 0, "missed_times": 0}
        return True

    def _duck_action(self, event, channel, user, action, setting):
        duck_timestamp = channel.duck_active
        xp_per_duck = 10
        duck_xp_modifier = 1

        got_duck = self._has_shot_duck(event, channel, user, action)
        if not got_duck:
            return False

        channel.set_setting("duck-last", time.time())
        channel.duck_active = None

        seconds = round(time.time() - duck_timestamp, 2)

        user_id = user.get_id()
        action_count = channel.get_user_setting(user_id, setting, 0)
        action_count += 1
        channel.set_user_setting(user_id, setting, action_count)

        ducks_plural = "duck" if action_count == 1 else "ducks"
        duck_special_lang = ""
        xp_text = ""

        if channel.duck_is_special:
            duck_special_info = SPECIAL_DUCKS[channel.duck_special_type][0]
            duck_xp_modifier = duck_special_info["xpbonus"]

            duck_special_lang = (
                "%s " % SPECIAL_DUCKS[channel.duck_special_type][0]["lang"]
            )

        if channel.get_setting("xp-enabled", False):
            xp = round(xp_per_duck * duck_xp_modifier)
            channel_id = channel.id
            channel_name = channel.name

            xpfrom, xpto = self.exports.get_one("xpaddinternal")(
                "%s:%s:%s:%s" % (user_id, channel_id, channel_name, xp)
            )
            if channel.get_setting("announce-xp-after-ducks", False):
                xp_text = " Your XP has increased from %s to %s!" % (
                    utils.irc.bold(xpfrom),
                    utils.irc.bold(xpto),
                )

        channel.duck_is_special = False

        return "%s %s a %sduck in %s seconds! You've %s %s %s in %s!%s" % (
            utils.irc.bold(user.nickname),
            action,
            duck_special_lang,
            utils.irc.bold(seconds),
            action,
            utils.irc.bold(utils.parse.comma_format(action_count)),
            ducks_plural,
            utils.irc.bold(channel.name),
            xp_text,
        )

    def _no_duck(self, channel, user, stderr):
        message = "There was no duck!"
        duck_timestamp = channel.get_setting("duck-last", None)

        if not duck_timestamp == None and channel.get_setting(
            "ducks-print-missed-time", False
        ):
            seconds = round(time.time() - duck_timestamp, 2)
            message += " The last duck was %s seconds ago!" % utils.irc.bold(
                seconds)

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
            action = self._duck_action(
                event, event["target"], event["user"], "befriended", "ducks-befriended"
            )
            if not action:
                return False

            event["stdout"].write(action)
        else:
            self._no_duck(event["target"], event["user"], event["stderr"])

    @utils.hook("received.command.bang", alias_of="trap")
    @utils.hook("received.command.trap")
    @utils.kwarg("help", "Shoot a duck")
    @utils.spec("!-channelonly")
    def trap(self, event):
        if event["target"].duck_active:
            action = self._duck_action(
                event, event["target"], event["user"], "killed", "ducks-shot"
            )
            if not action:
                return False

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
        query = self._target(
            event["target"], event["is_channel"], event["spec"][0])

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
        query = self._target(
            event["target"], event["is_channel"], event["spec"][0])

        stats = self._top_duck_stats(
            event["server"], event["target"], "ducks-shot", "enemies", query
        )
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
            convert_key=lambda n: utils.irc.bold(
                self._get_nickname(server, target, n)),
            value_format=lambda v: utils.parse.comma_format(v),
        )

        return "Top duck %s%s: %s" % (
            description,
            channel_query_str,
            ", ".join(top_10),
        )

    @utils.hook("received.command.duckaccuracy")
    @utils.kwarg("help", "Show your duck accuracy.")
    def get_accuracy(self, event):
        befs = event["user"].get_channel_settings_per_setting(
            "ducks-befriended")
        traps = event["user"].get_channel_settings_per_setting("ducks-shot")

        if not befs and not traps:
            event["stderr"].write("You've never interacted with ducks before!")
            return

        all = [(chan, val, "bef") for chan, val in befs]
        all += [(chan, val, "trap") for chan, val in traps]

        duck_miss_chance = event["target"].get_setting(
            "ducks-miss-chance", DEFAULT_MISS_CHANCE
        )

        current = {"bef": 0, "trap": 0}
        overall = {"bef": 0, "trap": 0}

        for channel_name, value, action in all:
            if not action in overall:
                overall[action] = 0
            overall[action] += value

            if event["is_channel"]:
                channel_name_lower = event["server"].irc_lower(channel_name)
                if channel_name_lower == event["target"].name:
                    current[action] = value

        accuracy = 66 * (current[action] + overall[action]) / 100
        duck_miss_chance = accuracy

        accuracyStr = round(duck_miss_chance, 2)
        accuracyStr = str(accuracyStr)
        accuracyStr = accuracyStr.rsplit("0")[0] if accuracyStr != "0" else "0"

        event["stdout"].write(
            "Accuracy bonus for %s: %s" % (
                utils.irc.bold(event["user"]), (accuracyStr))
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

        current = {"bef": 0, "trap": 0}
        overall = {"bef": 0, "trap": 0}

        if event["is_channel"]:
            for channel_name, value, action in all:
                if not action in overall:
                    overall[action] = 0
                overall[action] += value

                if event["is_channel"]:
                    channel_name_lower = event["server"].irc_lower(
                        channel_name)
                    if channel_name_lower == event["target"].name:
                        current[action] = value

        current_str = ""
        if current:
            current_str = " (%s Befriended, %s Killed in %s)" % (
                utils.irc.bold(utils.parse.comma_format(current["bef"])),
                utils.irc.bold(utils.parse.comma_format(current["trap"])),
                utils.irc.bold(event["target"].name),
            )

        event["stdout"].write(
            "%s has befriended %s and killed %s ducks%s"
            % (
                utils.irc.bold(target_user.nickname),
                utils.irc.bold(utils.parse.comma_format(overall["bef"])),
                utils.irc.bold(utils.parse.comma_format(overall["trap"])),
                current_str,
            )
        )

    @utils.hook("received.command.setduckfriends")
    @utils.kwarg("permission", "setducks")
    @utils.kwarg("min_args", 2)
    @utils.kwarg("channel_only", True)
    def setduckfriends(self, event):

        target_user = event["server"].get_user(event["args_split"][0])
        amount = int(event["args_split"][1])

        user_id = target_user.get_id()
        event["target"].set_user_setting(user_id, "ducks-befriended", amount)

        event["stdout"].write(
            "Set %s's befriended ducks to %d" % (target_user, amount))

    @utils.hook("received.command.setduckenemies")
    @utils.kwarg("permission", "setducks")
    @utils.kwarg("min_args", 2)
    @utils.spec("!-channelonly")
    def setduckenemies(self, event):

        target_user = event["server"].get_user(event["args_split"][0])
        amount = int(event["args_split"][1])

        user_id = target_user.get_id()
        event["target"].set_user_setting(user_id, "ducks-shot", amount)

        event["stdout"].write("Set %s's killed ducks to %d" %
                              (target_user, amount))

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
