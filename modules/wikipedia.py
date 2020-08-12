#--depends-on commands

import re

from src import ModuleManager, utils


URL_WIKIPEDIA = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_REGEX = re.compile("https?://en.wikipedia.org/wiki/([^/]+)")


@utils.export(
    "channelset",
    utils.BoolSetting("auto-wiki",
                      "Disable/Enable automatically getting info from wikipedia URLs")
)
class Module(ModuleManager.BaseModule):

    @utils.hook("command.regex")
    @utils.kwarg("expect_output", False)
    @utils.kwarg("ignore_action", True)
    @utils.kwarg("command", "wikipedia-trigger")
    @utils.kwarg("pattern", WIKIPEDIA_REGEX)
    def channel_message(self, event):
        if not event["target"].get_setting("auto-wiki", False):
            return

        event.eat()

        link = event["match"]
        self.wikipedia(event, link.group(1))

    @utils.hook("received.command.wi", alias_of="wiki")
    @utils.hook("received.command.wiki", alias_of="wikipedia")
    @utils.hook("received.command.wikipedia")
    @utils.kwarg("help", "Get information from wikipedia")
    @utils.spec("!<term>lstring")
    def wikipedia(self, event, title=None):
        incoming_title = title if "spec" not in event else event["spec"][0]
        incoming_title = incoming_title.replace("_", " ").replace("%27", "'")

        page = utils.http.request(
            URL_WIKIPEDIA,
            get_params={
                "action": "opensearch",
                "search": incoming_title,
                "limit": "1",
                "format": "json"
            }
        ).json()

        result = False if not page[1] else page[1][0]

        if result:
            page = utils.http.request(
                URL_WIKIPEDIA,
                get_params={
                    "action": "query",
                    "prop": "extracts|info",
                    "inprop": "url",
                    "titles": result,
                    "exintro": "true",
                    "explaintext": "true",
                    "exchars": "275",
                    "redirects": "",
                    "format": "json"
                }
            ).json()
        else:
            page = False

        if page:

            pages = page["query"]["pages"]
            article = list(pages.items())[0][1]
            if not "missing" in article:
                title, info = article["title"], article["extract"]
                title = article["title"]
                info = utils.parse.line_normalise(article["extract"])
                url = article["fullurl"]

                event["stdout"].write("%s: %s — %s" % (utils.irc.bold(title), info, url))
            else:
                event["stderr"].write("No results found")
        else:
            event["stderr"].write("No results found")
