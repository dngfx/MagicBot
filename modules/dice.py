# --depends-on commands

import random
import re

from src import ModuleManager, utils


ERROR_FORMAT = "Incorrect format! Format must be [number]d[number], e.g. 1d20"
RE_DICE = re.compile(
    "^([1-9]\d*)?d([1-9]\d*)((?:\s*[-+][1-9]\d{,2})*)\s*$", re.I)
RE_MODIFIERS = re.compile("([-+]\d+)")

MAX_DICE = 6
MAX_SIDES = 100


class Module(ModuleManager.BaseModule):
    @utils.hook("received.command.roll")
    @utils.hook("received.command.dice", alias_of="roll")
    @utils.kwarg("help", "Roll dice DND-style")
    @utils.spec("?<1d20>pattern(^(\d+)d(\d+)((?:\s*[-+]\d+)*))")
    def roll_dice(self, event):
        dice_count, side_count = 1, 6
        roll = "1d6"
        modifiers = []

        if event["spec"][0]:
            dice_count = int(event["spec"][0].group(1) or "1")
            side_count = int(event["spec"][0].group(2))
            roll = event["spec"][0].group(0).split("d")
            roll = utils.irc.bold(roll[0]) + " dice with " + \
                utils.irc.bold(roll[1]) + " sides each"
            modifiers = RE_MODIFIERS.findall(event["spec"][0].group(3))

        if dice_count > MAX_DICE:
            raise utils.EventError("Max number of dice is %s" % MAX_DICE)
        if side_count > MAX_SIDES:
            raise utils.EventError("Max number of sides is %s" % MAX_SIDES)

        results = random.choices(range(1, side_count + 1), k=dice_count)

        total_n = sum(results)

        for modifier in modifiers:
            if modifier[0] == "+":
                total_n += int(modifier[1:])
            else:
                total_n -= int(modifier[1:])

        total = ""
        if len(results) > 1 or modifiers:
            total = " (%s %s)" % (utils.irc.bold(
                "Total:"), utils.irc.bold(total_n))

        results_str = ", ".join(utils.irc.bold(str(r)) for r in results)

        result_str_final = "Rolled %s and got %s%s" % (
            roll, results_str, total)

        if total_n == 420:
            result_str_final = utils.irc.color(
                result_str_final, utils.consts.GREEN
            )

        if total_n == 666:
            result_str_final = utils.irc.color(
                result_str_final, utils.consts.RED
            )

        event["stdout"].write(result_str_final)
