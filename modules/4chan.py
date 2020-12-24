# --depends-on commands

import datetime
import re

import flag

from src import ModuleManager, utils

REGEX_LINK = re.compile("https?://boards\.4chan(?:nel)?\.org/(\w+)/thread/(\d+)")
BOARD_LIST_URL = "https://a.4cdn.org/boards.json"
THREAD_URL = "https://a.4cdn.org/%s/thread/%s.json"
NSFW_TEXT = utils.irc.color(utils.irc.bold("(NSFW) "), utils.consts.RED)

CAPCODE_COLOUR = {
    "mod": utils.consts.PURPLE,
    "admin": utils.consts.RED,
    "admin_highlight": utils.consts.RED,
    "developer": utils.consts.BLUE,
    "founder": utils.consts.LIGHTGREEN,
    "manager": utils.consts.PINK,
}

POST_LOCKED_EMOJI = "🔒"
POST_STICKY_EMOJI = "📌"


@utils.export(
    "channelset",
    utils.BoolSetting("auto-4chan", "Auto parse 4chan URLs to display with info"),
)
class Module(ModuleManager.BaseModule):
    _board_list = None
    _name = "4chan"

    @utils.hook("command.regex")
    @utils.kwarg("ignore_action", False)
    # @utils.kwarg("priority", EventManager.PRIORITY_MONITOR)
    @utils.kwarg("command", "4chan")
    @utils.kwarg("pattern", REGEX_LINK)
    def channel_message(self, event):
        if not event["target"].get_setting("auto-4chan", False):
            return

        event.eat()

        if self._board_list == None:
            self._parse_board_list()

        link = event["match"]
        info = None

        board = link.group(1)
        threadno = link.group(2)

        if board not in self._board_list:
            event["stderr"].write("Board not found")
            return

        thread = utils.http.request(THREAD_URL % (board, threadno))

        if thread.code == 404:
            event["stderr"].write("Thread /%s/%s not found" % (board, threadno))
            return

        thread = thread.json()
        info = thread["posts"][0]

        if "archived" in info:
            event["stderr"].write("That thread has been archived")
            return

        post_number = info["no"]

        post_text = ""
        if "com" in info:
            post_text = info["com"].replace("<br>", " ")
            post_text = utils.http.strip_html(post_text)
            post_text = " — %s%s" % (
                utils.irc.bold("Post: "),
                ((post_text[:125] + "...") if len(post_text) > 128 else post_text),
            )

        closed = POST_LOCKED_EMOJI if "closed" in info else ""
        sticky = POST_STICKY_EMOJI if "sticky" in info else ""
        closed_sticky = ""

        if closed or sticky:
            closed_sticky = "%s%s — " % (closed, sticky)

        has_file = "filename" in info

        nsfw = NSFW_TEXT if self._board_list[board] == False else ""
        capcode = ""
        country_flag = ""
        subject_text = ""
        tripcode = ""
        poster_id = ""

        if "trip" in info:
            tripcode = info["trip"]

        if "country" in info and board != "pol":
            country_flag = " " + flag.flag(info["country"])

        if "capcode" in info:
            capcode_text = info["capcode"]
            capcode = utils.irc.bold(" ## " + capcode_text.capitalize())

        if "id" in info:
            poster_id = " (%s %s)" % (utils.irc.bold("ID:"), info["id"])

        name = "%s%s%s%s" % (
            utils.irc.bold(info["name"]),
            tripcode,
            capcode,
            country_flag,
        )

        color = (
            CAPCODE_COLOUR[capcode_text]
            if "capcode" in info
            else utils.irc.consts.GREEN
        )
        name = utils.irc.color(name, color) + poster_id

        if "sub" in info:
            st = info["sub"]
            st = (st[:50] + "...") if len(st) > 53 else st
            subject_text = " — %s" % utils.irc.bold(st)

        total_posters = info["unique_ips"]
        if total_posters > 1:
            total_posters = total_posters - 1
        total_replies = info["replies"]

        replies_text = (
            utils.irc.bold(total_replies)
            + " repl"
            + ("ies" if total_replies != 1 else "y")
        )
        unique_posters = (
            utils.irc.bold(total_posters)
            + " poster"
            + ("s" if total_posters != 1 else "")
        )

        time = datetime.datetime.utcfromtimestamp(info["time"]).strftime(
            "%a, %b %-d, %Y at %H:%M UTC"
        )

        build_output = "%s%s — %s/%s/%s%s — %s%s — %s by %s" % (
            nsfw,
            name,
            closed_sticky,
            board,
            post_number,
            subject_text,
            time,
            post_text,
            replies_text,
            unique_posters,
        )

        event["stdout"].write(build_output)
        return

    def _parse_board_list(self):
        board_list_raw = utils.http.request(BOARD_LIST_URL).json()
        board_list_json = board_list_raw["boards"]
        board_list_build = {}
        boards = len(board_list_json)

        for cur_board in range(boards):
            board = board_list_json[cur_board]
            board_list_build[board["board"]] = bool(board["ws_board"])

        self._board_list = board_list_build
        return
