#--depends-on commands
#--depends-on permissions
#--depends-on shorturl
#--require-config twitter-api-key
#--require-config twitter-api-secret
#--require-config twitter-access-token
#--require-config twitter-access-secret

import json, re, pprint
from src import ModuleManager, utils
from . import format
import tweepy
from tweepy.parsers import JSONParser
from src.Logging import Logger as log

_bot = None
_events = None
_exports = None
_log = None

REGEX_TWITTER_STATUS_URL = re.compile("https?://(?:www\.|mobile\.)?twitter.com/[^/]+/status/(\d+)", re.I)
REGEX_TWITTER_PROFILE_URL = re.compile("https?://(?:www\.|mobile\.)?twitter.com/(\w+)$", re.I)


def _get_follows():
    return _bot.database.channel_settings.find_by_setting("twitter-follow")


@utils.export("channelset", utils.BoolSetting("auto-tweet", "Enable/disable automatically getting tweet info"))
class Module(ModuleManager.BaseModule):

    def on_load(self):
        auth = self._get_auth()
        api = self._get_api(auth)

    def _api(self):
        auth = self._get_auth()
        api = self._get_api(auth)
        return api

    def _get_auth(self):
        auth = tweepy.OAuthHandler(self.bot.config["twitter-api-key"], self.bot.config["twitter-api-secret"])
        auth.set_access_token(self.bot.config["twitter-access-token"], self.bot.config["twitter-access-secret"])
        return auth

    def _get_api(self, auth):
        return tweepy.API(auth, parser=JSONParser())

    def _from_id(self, tweet_id):
        api = self._api()
        try:
            status = api.get_status(tweet_id, tweet_mode="extended")
        except:
            return False

        return status

    def _get_profile(self, profile_name):
        api = self._api()

        try:
            profile = api.user_timeline(screen_name=profile_name, count=1, tweet_mode="extended")
        except:
            return False

        return profile[0]

    @utils.hook("received.command.tw", alias_of="tweet")
    @utils.hook("received.command.tweet")
    @utils.spec("!<tweet>string")
    def tweet(self, event):
        """
        :help: Get/find a tweet
        :usage: [@username/URL/ID]
        """
        target = event["spec"][0]

        profile = re.search(REGEX_TWITTER_PROFILE_URL, target)
        if profile or target.startswith("@"):
            profilematch = target[1:] if target.startswith("@") else profile.group(1)
            self.regex_profile(event, profilematch)
            return

        status = re.search(REGEX_TWITTER_STATUS_URL, target)
        if status or target.isdigit():
            statusmatch = target if target.isdigit() else status.group(1)
            self.regex_status(event, statusmatch)
            return

    @utils.hook("command.regex")
    @utils.kwarg("ignore_action", False)
    @utils.kwarg("command", "tweet")
    @utils.kwarg("pattern", REGEX_TWITTER_STATUS_URL)
    def regex_status(self, event, status=None):
        if not event["target"].get_setting("auto-tweet", False) and status == None:
            return

        event.eat()
        tweet_id = status if status else event["match"].group(1)
        tweet = self._from_id(tweet_id)

        if tweet:
            tweet_str = format._tweet(self.exports, event["server"], tweet, from_url=True)
            event["stdout"].write(tweet_str)
        else:
            event["stderr"].write("Could not find tweet")

    @utils.hook("command.regex")
    @utils.kwarg("ignore_action", False)
    @utils.kwarg("command", "tweet")
    @utils.kwarg("pattern", REGEX_TWITTER_PROFILE_URL)
    def regex_profile(self, event, profile=None):
        if not event["target"].get_setting("auto-tweet", False) and profile == None:
            return

        event.eat()

        twitter_profile = profile if profile else event["match"].group(1)

        profile = self._get_profile(twitter_profile)

        if profile:
            profile = format._profile(self.exports, event, profile, from_url=True)
            event["stdout"].write(profile)
        else:
            event["stderr"].write("Could not find profile")
