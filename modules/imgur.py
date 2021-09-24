# --depends-on commands
# --depends-on config
# --require-config imgur-api-key
# --require-config imgur-api-secret

import datetime
import re

from hurry.filesize import alternative, size
from imgurpython import ImgurClient

from src import ModuleManager, utils

REGEX_IMAGE = re.compile("https?://(?:i\.)?imgur.com/(\w{2,})")
REGEX_ALBUM = re.compile("https?://(?:i\.)?imgur.com/a/(\w+)")
REGEX_GALLERY = re.compile("https?://imgur.com/gallery/(\w+)")

GALLERY_FORMAT = "%s%s%sA gallery with %s image%s, %s view%s, posted %s%s"
ALBUM_FORMAT = "%s%s%sAn album with %s image%s, %s view%s, posted %s%s"
IMAGE_FORMAT = "%s%s%sA %s image, %s, %sx%s, with %s view%s, posted %s%s"

URL_IMAGE = "https://api.imgur.com/3/image/%s"
URL_GALLERY = "https://api.imgur.com/3/gallery/%s"
URL_ALBUM = "https://api.imgur.com/3/album/%s"
URL_REHOST = "https://api.imgur.com/3/upload"

ARROW_UP = "↑"
ARROW_DOWN = "↓"

NSFW_TEXT = "(NSFW)"


@utils.export(
    "channelset",
    utils.BoolSetting(
        "auto-imgur", "Disable/Enable automatically getting info from Imgur URLs"
    ),
)
class Module(ModuleManager.BaseModule):
    @utils.hook("command.regex")
    @utils.kwarg("ignore_action", False)
    @utils.kwarg("command", "imgur")
    @utils.kwarg("pattern", REGEX_IMAGE)
    def _regex_image(self, event):
        if event["target"].get_setting("auto-imgur", False):
            if event["match"].group(1) == "gallery":
                gallery_str = REGEX_GALLERY.match(event["match"].string)
                self._parse_gallery(event, gallery_str.group(1))
                event.eat()
                return True

            self._parse_image(event, event["match"].group(1))
            event.eat()
            return True

    @utils.hook("command.regex")
    @utils.kwarg("ignore_action", False)
    @utils.kwarg("command", "imgur")
    @utils.kwarg("pattern", REGEX_GALLERY)
    def _regex_gallery(self, event):
        if event["target"].get_setting("auto-imgur", False):
            self._parse_gallery(event, event["match"].group(1))
            event.eat()

    @utils.hook("command.regex")
    @utils.kwarg("ignore_action", False)
    @utils.kwarg("command", "imgur")
    @utils.kwarg("pattern", REGEX_ALBUM)
    def _regex_album(self, event):
        if event["target"].get_setting("auto-imgur", False):
            self._parse_album(event, event["match"].group(1))
            event.eat()

    def _parse_gallery(self, event, hash):
        api_key = self.bot.config["imgur-api-key"]
        result = utils.http.request(
            URL_GALLERY % hash, headers={"Authorization": "Client-ID %s" % api_key}
        )

        if result.code == 404:
            event["stderr"].write("Image %s not found." % hash)
            return False

        result = result.json()

        if not result or ("status" in result and result["status"] != 200):
            event["stderr"].write("Error decoding response.")
            return False

        data = result["data"]

        nsfw = ("%s " % utils.irc.color(utils.irc.bold(NSFW_TEXT), utils.consts.RED)) if data["nsfw"] == True else ""
        title = ("%s " % data["title"]) if data["title"] else ""
        views = data["views"]
        views_plural = "" if views == 1 else "s"
        time = datetime.datetime.utcfromtimestamp(data["datetime"]).strftime(
            "%e %b, %Y at %H:%M"
        )
        images = data["images_count"]
        image_plural = "" if images == 1 else "s"

        bracket_left = "(" if title or nsfw else ""
        bracket_right = ")" if title or nsfw else ""

        output = GALLERY_FORMAT % (
            nsfw,
            utils.irc.bold(title),
            bracket_left,
            utils.irc.bold(images),
            image_plural,
            utils.irc.bold(views),
            utils.irc.bold(time),
            bracket_right,
        )

        event["stdout"].write(output)

    def _parse_album(self, event, hash):
        api_key = self.bot.config["imgur-api-key"]
        result = utils.http.request(
            URL_ALBUM % hash, headers={"Authorization": "Client-ID %s" % api_key}
        )

        if result.code == 404:
            event["stderr"].write("Image %s not found." % hash)
            return False

        result = result.json()

        if not result or ("status" in result and result["status"] != 200):
            event["stderr"].write("Error decoding response.")
            return False

        data = result["data"]

        nsfw = ("%s " % utils.irc.color(utils.irc.bold(NSFW_TEXT), utils.consts.RED)) if data["nsfw"] == True else ""
        title = ("%s " % data["title"]) if data["title"] else ""
        views = data["views"]
        views_plural = "" if views == 1 else "s"
        time = datetime.datetime.utcfromtimestamp(data["datetime"]).strftime(
            "%e %b, %Y at %H:%M"
        )
        images = data["images_count"]
        image_plural = "" if images == 1 else "s"

        bracket_left = "(" if title or nsfw else ""
        bracket_right = ")" if title or nsfw else ""

        output = ALBUM_FORMAT % (
            nsfw,
            utils.irc.bold(title),
            bracket_left,
            utils.irc.bold(images),
            image_plural,
            utils.irc.bold(views),
            views_plural,
            utils.irc.bold(time),
            bracket_right,
        )

        event["stdout"].write(output)

    def _parse_image(self, event, hash):
        api_key = self.bot.config["imgur-api-key"]
        result = utils.http.request(
            URL_IMAGE % hash, headers={"Authorization": "Client-ID %s" % api_key}
        )

        if result.code == 404:
            event["stderr"].write("Image %s not found." % hash)
            return False

        result = result.json()

        if not result or ("status" in result and result["status"] != 200):
            event["stderr"].write("Error decoding response.")
            return False

        data = result["data"]

        nsfw = ("%s " % utils.irc.color(utils.irc.bold(NSFW_TEXT), utils.consts.RED)) if data["nsfw"] == True else ""
        title = ("%s " % data["title"]) if data["title"] else ""
        views = data["views"]
        views_plural = "" if views == 1 else "s"
        time = datetime.datetime.utcfromtimestamp(data["datetime"]).strftime(
            "%e %b, %Y at %H:%M"
        )
        mime = data["type"].split("/")[-1]
        width = data["width"]
        height = data["height"]
        fsize = size(data["size"], system=alternative)

        bracket_left = "(" if title or nsfw else ""
        bracket_right = ")" if title or nsfw else ""

        output = IMAGE_FORMAT % (
            nsfw,
            title,
            bracket_left,
            utils.irc.bold(mime),
            utils.irc.bold(fsize),
            width,
            height,
            utils.irc.bold(views),
            views_plural,
            utils.irc.bold(time),
            bracket_right,
        )

        event["stdout"].write(output)

    @utils.hook("received.command.rehost", channel_only=True)
    @utils.kwarg("permission", "rehost")
    def rehost(self, event):
        channel = event["target"]
        args = event["args_split"]

        if len(args) is not 1:
            event["stderr"].write("You must provide exactly one link to rehost.")
            return

        url = args[0]

        imgur_client = ImgurClient(
            self.bot.config["imgur-api-key"], self.bot.config["imgur-api-secret"]
        )

        upload = imgur_client.upload_from_url(url, config=None, anon=True)

        if upload["link"] is not "":
            event["stdout"].write("Your image was rehosted. URL: %s" % upload["link"])
        else:
            event["stderr"].write("Image upload unsuccessful")
