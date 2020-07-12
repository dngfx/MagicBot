#--depends-on commands

import hashlib, re, urllib.parse, datetime
from src import EventManager, ModuleManager, utils

REGEX_LINK = re.compile("https?://(?:\w+\.)?reddit.com/r/([^/]+)/comments/([^/ ]+)")
REGEX_SUBREDDIT_LINK = re.compile("https?://(?:\w+\.)?reddit.com/r/([^/]+)(?:[ /$])")
SANE_URL = "https://www.reddit.com/r/%s/comments/%s.json"
NSFW_TEXT = utils.irc.bold(utils.irc.color(" (NSFW)", utils.consts.RED))
ARROW_UP = "↑"
ARROW_DOWN = "↓"


@utils.export("channelset", utils.BoolSetting("auto-reddit", "Auto parse Reddit URLs to display with info"))
class Module(ModuleManager.BaseModule):

    @utils.hook("command.regex")
    @utils.kwarg("ignore_action", False)
    #@utils.kwarg("priority", EventManager.PRIORITY_MONITOR)
    @utils.kwarg("command", "reddit")
    @utils.kwarg("pattern", REGEX_LINK)
    def channel_message(self, event):
        if event["target"].get_setting("auto-reddit", False):
            event.eat()
            link = event["match"]
            subreddit = link.group(1)
            thread_id = link.group(2)

            thread_info = utils.http.request(SANE_URL % (subreddit, thread_id)).json()
            thread = thread_info[0]["data"]["children"][0]["data"]

            title = (thread["title"][:45] + "...") if len(thread["title"]) > 45 else thread["title"]
            upvotes = thread["ups"]
            author = thread["author"]
            downvotes = thread["downs"]
            nsfw = NSFW_TEXT if thread["over_18"] else ""
            time = datetime.datetime.utcfromtimestamp(thread["created_utc"]). \
                strftime("%a, %b %-d, %Y at %H:%M UTC")
            np_subreddit = thread["subreddit_name_prefixed"]
            comments = "1 comment" if thread["num_comments"] == 1 else ("%s comments" % thread["num_comments"])

            upvote_arrow = utils.irc.bold(utils.irc.color(ARROW_UP, utils.consts.GREEN))
            downvote_arrow = utils.irc.bold(utils.irc.color(ARROW_DOWN, utils.consts.RED))

            stdout = event["stdout"]
            stdout.write("%s%s (%s) — Posted by %s to %s on %s — %s %s" % (utils.irc.bold(title),
                                                                           nsfw,
                                                                           comments,
                                                                           author,
                                                                           np_subreddit,
                                                                           time,
                                                                           upvotes,
                                                                           upvote_arrow))

        #nightmare
        return
