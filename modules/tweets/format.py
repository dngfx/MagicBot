import datetime
import html
import time
from datetime import datetime, timezone

from src import utils


# @elonmusk - Elon Musk 😎 ✓ - Created Jun 2009 - 11.7K Tweets - 47.M Followers, Following 96

VERIFIED_TICK = utils.irc.color(" ✅", utils.consts.LIGHTBLUE)
FORMAT_PROFILE_PAGE = "%s — %s%s — Created %s — %s Tweets — %s Followers, Following %s — %s: %s — %s"


def _timestamp(dt):
    dt = datetime.strptime(dt, '%a %b %d %H:%M:%S %z %Y')
    seconds_since = time.time() - dt.timestamp()
    timestamp = utils.datetime.format.to_pretty_since(seconds_since, max_units=2)
    return "%s ago" % timestamp


def _normalise(tweet):
    return html.unescape(utils.parse.line_normalise(tweet))


def _tweet(exports, event, tweet, from_url):
    user = tweet["user"]
    linked_id = tweet["id"]
    username = user["screen_name"]

    verified = VERIFIED_TICK if user["verified"] else ""

    tweet_link = "https://twitter.com/%s/status/%s" % (username, linked_id)

    short_url = ""
    if not from_url:
        short_url = exports.get_one("shorturl")(event["server"], tweet_link, context=event["target"])
        short_url = " - %s" % short_url if short_url else ""
        created_at = _timestamp(tweet["created_at"])

        if get_shorturl:
            short_url = get_shorturl

    # having to use hasattr here is nasty.
    if hasattr(tweet, "retweeted_status"):
        original_username = tweet["retweeted_status"]["user"]["screen_name"]
        original_text = tweet["retweeted_status"]["full_text"]
        original_timestamp = _timestamp(tweet["retweeted_status"]["created_at"])
        return "(@%s%s (%s) retweeted @%s (%s)) %s%s" % (
            username,
            verified,
            created_at,
            original_username,
            original_timestamp,
            _normalise(original_text),
            short_url
        )
    else:
        return "(@%s%s, %s) %s%s" % (username, verified, created_at, _normalise(tweet["full_text"]), short_url)


def _profile(exports, event, profile, from_url):
    user = profile["user"]

    profile_id = profile["id"]
    profile_username = "@" + user["screen_name"]
    profile_display_name = user["name"]
    total_tweets = utils.parse.shorten_volume(user["statuses_count"])
    verified = VERIFIED_TICK if user["verified"] else ""
    following = utils.parse.shorten_volume(user["friends_count"])
    followers = utils.parse.shorten_volume(user["followers_count"])
    created_at = user["created_at"]
    created_at_hr = datetime.strptime(created_at,
                                      '%a %b %d %H:%M:%S %z %Y').replace(tzinfo=timezone.utc
                                                                         ).astimezone(tz=None).strftime('%b %Y')

    latest_tweet = _normalise(profile["full_text"])

    return FORMAT_PROFILE_PAGE % (
        utils.irc.bold(profile_username),
        profile_display_name,
        verified,
        utils.irc.bold(created_at_hr),
        utils.irc.bold(total_tweets),
        utils.irc.bold(followers),
        utils.irc.bold(following),
        utils.irc.bold("Latest Tweet"),
        latest_tweet,
        utils.irc.bold(("https://twitter.com/%s" % user["screen_name"]))
    )
