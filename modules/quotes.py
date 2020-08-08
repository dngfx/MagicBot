#--depends-on commands

import random, time, pprint, re
from src import EventManager, ModuleManager, utils


@utils.export(
    "channelset",
    utils.BoolSetting("channel-quotes",
                      "Whether or not quotes added from this channel are kept in this channel")
)
@utils.export("channelset", utils.BoolSetting("phil-ken-sebben", "HA HA HA!"))
class Module(ModuleManager.BaseModule):

    def category_and_quote(self, s):
        category, sep, quote = s.partition("=")
        category = category.strip()

        if not sep:
            return category, None
        return category, quote.strip()

    def _get_quotes(self, target, category):
        return target.get_setting("quotes-%s" % category, [])

    def _set_quotes(self, target, category, quotes):
        target.set_setting("quotes-%s" % category, quotes)

    @utils.hook("received.command.qadd", alias_of="quoteadd")
    @utils.hook("received.command.quoteadd", min_args=1)
    @utils.kwarg("help", "Add a quote to a category")
    @utils.kwarg("usage", "<category> = <quote>")
    def quote_add(self, event):
        category, quote = self.category_and_quote(event["args"])
        if category and quote:
            target = event["server"]
            if event["is_channel"] and event["target"].get_setting("channel-quotes", False):
                target = event["target"]

            quotes = self._get_quotes(target, category)
            quotes.append([event["user"].name, int(time.time()), quote])
            self._set_quotes(target, category, quotes)

            event["stdout"].write("Quote added")
        else:
            event["stderr"].write("Please provide a category AND quote")

    def _target_zip(self, target, quotes):
        return [[u, t, q, target] for u, t, q in quotes]

    @utils.hook("received.command.qdel", alias_of="quotedel")
    @utils.hook("received.command.quotedel", min_args=1)
    @utils.kwarg("help", "Delete a given quote from a given category")
    @utils.kwarg("usage", "<category> = <quote>")
    def quote_del(self, event):
        category, remove_quote = self.category_and_quote(event["args"])
        category = category or event["args"].strip()

        message = None
        quotes = self._target_zip(event["server"], self._get_quotes(event["server"], category))
        if event["is_channel"]:
            quotes += self._target_zip(event["target"], self._get_quotes(event["target"], category))
        quotes = sorted(quotes, key=lambda q: q[1])

        if not quotes:
            raise utils.EventError("Quote category '%s' not found" % category)

        found_target = None
        if not remove_quote == None:
            remove_quote_lower = remove_quote.lower()
            for nickname, time_added, quote, target in quotes[:]:
                if quote.lower() == remove_quote_lower:
                    quotes.remove([nickname, time_added, quote])
                    found_target = target
                    message = "Removed quote from '%s'"
                    break
        else:
            if quotes:
                quote = quotes.pop(-1)
                found_target = quote[-1]
                message = "Removed last '%s' quote"

        if not message == None:
            self._set_quotes(found_target, category, quotes)
            event["stdout"].write(message % category)
        else:
            event["stderr"].write("Quote not found")

    @utils.hook("command.regex")
    @utils.kwarg("expect_output", True)
    @utils.kwarg("ignore_action", True)
    @utils.kwarg("command", "philkensebben")
    @utils.kwarg("pattern", re.compile(".+"))
    def channel_message(self, event):
        if not event["target"].get_setting("phil-ken-sebben", False):
            return
        category = "phil ken sebben"
        quotes = event["server"].get_setting("quotes-%s" % category, [])
        if quotes and (random.randint(0, 99) < 3):
            index = random.randint(0, len(quotes) - 1)
            nickname, time_added, quote = quotes[index]

            event["stdout"].prefix = None
            event["stdout"].write("%s %s" % (utils.irc.bold("<PHIL KEN SEBBEN>"), quote))
            event.eat()

    @utils.hook("received.command.q", alias_of="quote")
    @utils.hook("received.command.quote", min_args=1)
    @utils.kwarg("help", "Get a random quote from a given category")
    @utils.kwarg("usage", "<category> [= <search>]")
    def quote(self, event):
        category, search = self.category_and_quote(event["args"])
        quotes = event["server"].get_setting("quotes-%s" % category, [])
        if event["is_channel"]:
            quotes += self._get_quotes(event["target"], category)

        if search:
            search_lower = search.lower()
            quotes = [q for q in quotes if search_lower in q[-1].lower()]

        if quotes:
            index = random.randint(0, len(quotes) - 1)
            nickname, time_added, quote = quotes[index]

            category_str = category
            if search:
                category_str = "%s (%s [%d found])" % (category_str, search, len(quotes))
            event["stdout"].write("%s: %s" % (category_str, quote))
        else:
            event["stderr"].write("No matching quotes")

    @utils.hook("received.command.grab", alias_of="quotegrab")
    @utils.hook("received.command.quotegrab", min_args=1, channel_only=True)
    @utils.kwarg("help", "Grab the latest 1-3 lines from a user and add them " "as a quote")
    @utils.kwarg("usage", "<nickname> [line-count]")
    def quote_grab(self, event):
        line_count = 1
        if len(event["args_split"]) > 1:
            line_count = utils.parse.try_int(event["args_split"][1])
            if not line_count or not (0 < line_count < 4):
                raise utils.EventError("Please provide a number between 1 and 3")

        target = event["args_split"][0]
        lines = event["target"].buffer.find_many_from(target, line_count)
        if lines:
            lines.reverse()
            target = event["server"]
            if event["target"].get_setting("channel-quotes", False):
                target = event["target"]

            quotes = self._get_quotes(target, target)

            lines_str = []
            for line in lines:
                lines_str.append(line.format())
            text = " ".join(lines_str)

            quotes.append([event["user"].name, int(time.time()), text])

            quote_category = line.sender
            if event["server"].has_user(quote_category):
                account = event["server"].get_user_nickname(event["server"].get_user(quote_category).get_id())

            self._set_quotes(target, quote_category, quotes)

            event["stdout"].write("Quote added")
        else:
            event["stderr"].write("Nothing found to quote")
