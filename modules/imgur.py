#--depends-on commands
#--depends-on config
#--require-config imgur-api-key

import re, datetime
from src import ModuleManager, utils, EventManager
from hurry.filesize import size, alternative

REGEX_IMAGE = re.compile("https?://(?:i\.)?imgur.com/(\w+)")
REGEX_GALLERY = re.compile("https?://imgur.com/gallery/(\w+)")

GALLERY_FORMAT = "%s%s%sA gallery with %s image%s, %s views, posted %s%s"
IMAGE_FORMAT = "%s%s%sA %s image, %s, %sx%s, with %s views, posted %s%s"

URL_IMAGE = "https://api.imgur.com/3/image/%s"
URL_GALLERY = "https://api.imgur.com/3/gallery/%s"

ARROW_UP = "↑"
ARROW_DOWN = "↓"

NSFW_TEXT = "(NSFW)"


@utils.export(
    "channelset", utils.BoolSetting("auto-imgur", "Disable/Enable automatically getting info from Imgur URLs")
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

    @utils.hook("command.regex")
    @utils.kwarg("ignore_action", False)
    @utils.kwarg("command", "imgur")
    @utils.kwarg("pattern", REGEX_GALLERY)
    def _regex_gallery(self, event):
        if event["target"].get_setting("auto-imgur", False):
            self._parse_gallery(event, event["match"].group(1))
            event.eat()

    def _parse_gallery(self, event, hash):
        api_key = self.bot.config["imgur-api-key"]
        result = utils.http.request(URL_GALLERY % hash, headers={"Authorization": "Client-ID %s" % api_key})

        if result.code == 404:
            event["stderr"].write("Image %s not found." % hash)
            return False

        result = result.json()

        if not result or ("status" in result and result["status"] != 200):
            event["stderr"].write("Error decoding response.")
            return False

        data = result["data"]

        nsfw = ("%s " % utils.irc.bold(NSFW_TEXT)) if data["nsfw"] == True else ""
        title = ("%s " % data["title"]) if data["title"] else ""
        views = data["views"]
        time = datetime.datetime.utcfromtimestamp(data["datetime"]).strftime("%e %b, %Y at %H:%M")
        images = data["images_count"]
        image_plural = "" if images == 1 else "s"

        bracket_left = "(" if title or nsfw else ""
        bracket_right = ")" if title or nsfw else ""

        output = GALLERY_FORMAT % (
            nsfw, utils.irc.bold(title), bracket_left, utils.irc.bold(images), image_plural, utils.irc.bold(views),
            utils.irc.bold(time), bracket_right
        )

        event["stdout"].write(output)

    def _parse_image(self, event, hash):
        api_key = self.bot.config["imgur-api-key"]
        result = utils.http.request(URL_IMAGE % hash, headers={"Authorization": "Client-ID %s" % api_key})

        if result.code == 404:
            event["stderr"].write("Image %s not found." % hash)
            return False

        result = result.json()

        if not result or ("status" in result and result["status"] != 200):
            event["stderr"].write("Error decoding response.")
            return False

        data = result["data"]

        nsfw = ("%s " % utils.irc.bold(NSFW_TEXT)) if data["nsfw"] == True else ""
        title = ("%s " % data["title"]) if data["title"] else ""
        views = data["views"]
        time = datetime.datetime.utcfromtimestamp(data["datetime"]).strftime("%e %b, %Y at %H:%M")
        mime = data["type"].split("/")[-1]
        width = data["width"]
        height = data["height"]
        fsize = size(data["size"], system=alternative)

        bracket_left = "(" if title or nsfw else ""
        bracket_right = ")" if title or nsfw else ""

        output = IMAGE_FORMAT % (
            nsfw, title, bracket_left, utils.irc.bold(mime), utils.irc.bold(fsize), width, height,
            utils.irc.bold(views), utils.irc.bold(time), bracket_right
        )

        event["stdout"].write(output)


"""
{
    'data': {
        'id': '7PiHitE',
        'title': None,
        'description': None,
        'datetime': 1585303718,
        'type': 'image/jpeg',
        'animated': False,
        'width': 823,
        'height': 1279,
        'size': 163954,
        'views': 676,
        'bandwidth': 110832904,
        'vote': None,
        'favorite': False,
        'nsfw': False,
        'section': None,
        'account_url': None,
        'account_id': None,
        'is_ad': False,
        'in_most_viral': False,
        'has_sound': False,
        'tags': [],
        'ad_type': 0,
        'ad_url': '',
        'edited': '0',
        'in_gallery': False,
        'link': 'https://i.imgur.com/7PiHitE.jpg',
        'ad_config': {
            'safeFlags': ['not_in_gallery', 'share'],
            'highRiskFlags': [],
            'unsafeFlags': ['sixth_mod_unsafe'],
            'wallUnsafeFlags': [],
            'showsAds': False
        }
    },
    'success': True,
    'status': 200
}
"""
