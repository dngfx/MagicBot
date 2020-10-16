#--depends-on commands
#--depends-on config
#--depends-on permissions

import re
import time

from src import EventManager, ModuleManager, utils


KARMA_DELAY_SECONDS = 10

REGEX_WORD = re.compile(r"^([^(\s,:]+)(?:[:,])?\s*(\+\+|--)\s*$")
REGEX_WORD_START = re.compile(r"^(\+\+|--)(?:\s*)([^(\s,:]+)\s*$")
REGEX_PARENS = re.compile(r"\(([^)]+)\)(\+\+|--)")


@utils.export("channelset", utils.BoolSetting("karma-pattern", "Enable/disable parsing ++/-- karma format"))
class Module(ModuleManager.BaseModule):


    def _karma_str(self, karma):
        karma_str = str(karma)
        if karma < 0:
            return utils.irc.color(str(karma), utils.consts.RED)
        elif karma > 0:
            return utils.irc.color(str(karma), utils.consts.LIGHTGREEN)
        else:
            return utils.irc.color(str(karma), utils.consts.YELLOW)


    @utils.hook("new.user")
    def new_user(self, event):
        event["user"]._last_positive_karma = None
        event["user"]._last_negative_karma = None


    def _check_throttle(self, user, positive):
        bypass_throttle = user.get_setting("permissions", None)
        #if bypass_throttle != None and "*" in bypass_throttle:
            #return [True, KARMA_DELAY_SECONDS]

        timestamp = None
        if positive:
            timestamp = user._last_positive_karma
        else:
            timestamp = user._last_negative_karma
        return [(timestamp == None or (time.time() - timestamp) >= KARMA_DELAY_SECONDS), (KARMA_DELAY_SECONDS if timestamp is None else (KARMA_DELAY_SECONDS - int(time.time()-timestamp)))]


    def _set_throttle(self, user, positive):
        if positive:
            user._last_positive_karma = time.time()
        else:
            user._last_negative_karma = time.time()


    def _get_target(self, server, target):
        target = target.strip()
        if not " " in target and server.has_user(target):
            return server.get_user_nickname(server.get_user(target).get_id())
        return target.lower()


    def _change_karma(self, server, sender, target, positive):
        throttle, wait = self._check_throttle(sender, positive)
        print(throttle, wait)
        if not throttle:
            return False, "Try again in about %d seconds" % wait

        target = utils.irc.strip_font(target)
        nick = target
        target = self._get_target(server, target)

        if target == "":
            return False, "You cannot set karma for nothing!"

        if sender.nickname.lower() == target.lower():
            return False, "You cannot set karma for yourself"

        setting = "karma-%s" % target
        karma = sender.get_setting(setting, 0)
        karma += 1 if positive else -1

        if karma == 0:
            sender.del_setting(setting)
        else:
            sender.set_setting(setting, karma)

        self._set_throttle(sender, positive)
        karma_str = self._karma_str(karma)

        karma_total = self._karma_str(self._get_karma(server, target))

        return True, "%s now has %s karma (%s from %s)" % (nick, karma_total, karma_str, sender.nickname)


    @utils.hook("received.command.setkarma")
    @utils.kwarg("min_args", 2)
    @utils.kwarg("permission", "setkarma")
    def set_karma(self, event):
        server = event["server"]
        karma_ev = event["args_split"][1:]
        karma_text = " ".join(karma_ev)
        karma = "karma-%s" % karma_text
        amount = int(event["args_split"][0])

        sender = event["user"]
        sender.set_setting(karma, amount)

        event["stdout"].write("Set %s karma to %s" % (karma_text, amount))


    @utils.hook("command.regex", pattern=REGEX_WORD)
    @utils.hook("command.regex", pattern=REGEX_PARENS)
    @utils.kwarg("command", "karma")
    @utils.kwarg("priority", EventManager.PRIORITY_HIGH)
    # high priority to make `++asd++` count as `++` on `++help`
    def regex_word(self, event):
        if event["target"].get_setting("karma-pattern", False):
            event.eat()

            target = event["match"].group(1)
            positive = event["match"].group(2) == "++"
            success, message = self._change_karma(event["server"], event["user"], target, positive)
            event["stdout" if success else "stderr"].write(message)


    @utils.hook("command.regex", pattern=REGEX_WORD_START)
    @utils.kwarg("command", "karma")
    def regex_word_start(self, event):
        if event["target"].get_setting("karma-pattern", False):
            target = event["match"].group(2)
            positive = event["match"].group(1) == "++"
            success, message = self._change_karma(event["server"], event["user"], target, positive)
            event["stdout" if success else "stderr"].write(message)

    @utils.hook("received.command.karma+", alias_of="addpoint")
    @utils.hook("received.command.addpoint")
    @utils.hook("received.command.karma-", alias_of="rmpoint")
    @utils.hook("received.command.rmpoint")
    @utils.kwarg("min_args", 1)
    @utils.spec("!<target>string")
    def changepoint(self, event):
        if event["command"] == "addpoint" or event["command"] == "karma+":
            positive = True
        else:
            positive = False
        success, message = self._change_karma(event["server"], event["user"], event["spec"][0], positive)
        event["stdout" if success else "stderr"].write(message)


    @utils.hook("received.command.karma")
    def karma(self, event):
        """
        :help: Get your or someone else's karma
        :usage: [target]
        """
        if event["args"]:
            target = event["args"]
        else:
            target = event["user"].nickname

        target = self._get_target(event["server"], target)
        karma = self._karma_str(self._get_karma(event["server"], target))

        event["stdout"].write("%s has %s karma" % (target, karma))


    def _get_karma(self, server, target):
        settings = dict(server.get_all_user_settings("karma-%s" % target))

        target_lower = server.irc_lower(target)
        if target_lower in settings:
            del settings[target_lower]

        return sum(settings.values())


    @utils.hook("received.command.resetkarma")
    @utils.kwarg("min_args", 2)
    @utils.kwarg("help", "Reset a specific karma to 0")
    @utils.kwarg("permission", "resetkarma")
    @utils.kwarg("channel_only", True)
    @utils.spec("!'by !<nickname>ouser")
    @utils.spec("!'for !<target>string")
    def reset_karma(self, event):
        subcommand = event["spec"][0]

        if subcommand == "by":
            target_user = event["spec"][1]
            karma = target_user.find_setting(prefix="karma-")
            for setting, _ in karma:
                target_user.del_setting(setting)

            if karma:
                event["stdout"].write("Cleared karma by %s" % target_user.nickname)
            else:
                event["stderr"].write("No karma to clear by %s" % target_user.nickname)
        elif subcommand == "for":
            setting = "karma-%s" % event["spec"][1]
            karma = event["server"].get_all_user_settings(setting)
            for nickname, value in karma:
                user = event["server"].get_user(nickname)
                user.del_setting(setting)

            if karma:
                event["stdout"].write("Cleared karma for %s" % event["spec"][1])
            else:
                event["stderr"].write("No karma to clear for %s" % event["spec"][1])
        else:
            raise utils.EventError("Unknown subcommand '%s'" % subcommand)


    @utils.hook("received.command.topkarma", channel_only=True)
    @utils.kwarg("help", "Show top 10 people with karma in the channel")
    def topkarma(self, event):
        stats = self._top_karma_stats(event["server"], event["target"], True)
        event["stdout"].write(stats)

    @utils.hook("received.command.bottomkarma", channel_only=True)
    @utils.kwarg("help", "Show bottom 10 people with karma in the channel")
    def bottomkarma(self, event):
        stats = self._top_karma_stats(event["server"], event["target"], False)
        event["stdout"].write(stats)

    def _karma_target(self, target, is_channel, query):
        if query:
            if not query == "*":
                return query
        elif is_channel:
            return target.name

    def _get_all_karma(self, event, order):
        order = "AND value > 0" if order is True else "AND value < 0"
        return self.bot.database.execute_fetchall(("SELECT user_id, setting, value from user_settings WHERE setting LIKE 'karma-%%' %s" % order))

    def _top_karma_stats(self, server, target, order):
        sort_order = "Highest" if order is True else "Lowest"
        color = utils.irc.consts.GREEN if order is True else utils.irc.consts.RED
        stats = self._get_all_karma(target, order)

        karma_stats = {}
        for item in stats:
            userid, karma, amount = item
            amount = int(amount)
            karma_name = karma.split("-")[1]
            if karma_name in karma_stats:
                karma_stats[karma_name] = karma_stats[karma_name] + amount
            else:
                karma_stats[karma_name] = amount

        sort_karma = utils.top_10(karma_stats, convert_key=lambda n: utils.irc.bold(n), value_format=lambda n: utils.irc.color(n, color))

        #top_10 = utils.top_10(user_stats, convert_key=lambda n: utils.irc.bold(self._get_nickname(server, target, n)), )
        return "%s karma: %s" % (sort_order, ", ".join(sort_karma))
