import datetime, html, time, pprint
from src import utils
from var_dump import var_export
from datetime import datetime
from datetime import timezone

# @elonmusk - Elon Musk 😎 ✓ - Created Jun 2009 - 11.7K Tweets - 47.M Followers, Following 96

VERIFIED_TICK = utils.irc.color(" ✅", utils.consts.LIGHTBLUE)
FORMAT_PROFILE_PAGE = "%s — %s%s — Created %s — %s Tweets — %s Followers, Following %s%s"


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

    created_at = _timestamp(tweet["created_at"])

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


""" {
    'created_at': 'Sat Jul 25 21:40:42 +0000 2020',
    'id': 1287140748241047554,
    'id_str': '1287140748241047554',
    'full_text': 'Cool Model 3 review by @iamjamiefoxx https://t.co/hJDD7BjkE3',
    'truncated': False,
    'display_text_range': [0,
                           60],
    'entities':
        {
            'hashtags': [],
            'symbols': [],
            'user_mentions':
                [
                    {
                        'screen_name': 'iamjamiefoxx',
                        'name': 'Jamie Foxx',
                        'id': 138600717,
                        'id_str': '138600717',
                        'indices': [23,
                                    36]
                    }
                ],
            'urls':
                [
                    {
                        'url': 'https://t.co/hJDD7BjkE3',
                        'expanded_url': 'https://m.youtube.com/watch?v=tB15Da2TRWw&feature=youtu.be',
                        'display_url': 'm.youtube.com/watch?v=tB15Da…',
                        'indices': [37,
                                    60]
                    }
                ]
        },
    'source': '<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>',
    'in_reply_to_status_id': None,
    'in_reply_to_status_id_str': None,
    'in_reply_to_user_id': None,
    'in_reply_to_user_id_str': None,
    'in_reply_to_screen_name': None,
    'user':
        {
            'id': 44196397,
            'id_str': '44196397',
            'name': 'Elon Musk',
            'screen_name': 'elonmusk',
            'location': '',
            'description': '',
            'url': None,
            'entities': {
                'description': {
                    'urls': []
                }
            },
            'protected': False,
            'followers_count': 37171697,
            'friends_count': 97,
            'listed_count': 54490,
            'created_at': 'Tue Jun 02 20:12:29 +0000 2009',
            'favourites_count': 6194,
            'utc_offset': None,
            'time_zone': None,
            'geo_enabled': False,
            'verified': True,
            'statuses_count': 11777,
            'lang': None,
            'contributors_enabled': False,
            'is_translator': False,
            'is_translation_enabled': False,
            'profile_background_color': 'C0DEED',
            'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme1/bg.png',
            'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme1/bg.png',
            'profile_background_tile': False,
            'profile_image_url': 'http://pbs.twimg.com/profile_images/1276417699032137728/QGSGH8FZ_normal.jpg',
            'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1276417699032137728/QGSGH8FZ_normal.jpg',
            'profile_banner_url': 'https://pbs.twimg.com/profile_banners/44196397/1576183471',
            'profile_link_color': '0084B4',
            'profile_sidebar_border_color': 'C0DEED',
            'profile_sidebar_fill_color': 'DDEEF6',
            'profile_text_color': '333333',
            'profile_use_background_image': True,
            'has_extended_profile': True,
            'default_profile': False,
            'default_profile_image': False,
            'following': True,
            'follow_request_sent': False,
            'notifications': False,
            'translator_type': 'none'
        },
    'geo': None,
    'coordinates': None,
    'place': None,
    'contributors': None,
    'is_quote_status': False,
    'retweet_count': 461,
    'favorite_count': 5288,
    'favorited': False,
    'retweeted': False,
    'possibly_sensitive': False,
    'possibly_sensitive_appealable': False,
    'lang': 'en'
} """


def _profile(exports, event, profile, from_url):
    user = profile["user"]

    profile_id = profile["id"]
    profile_username = "@" + user["screen_name"]
    profile_display_name = user["name"]
    total_tweets = utils.parse._shorten_volume(user["statuses_count"])
    verified = VERIFIED_TICK if user["verified"] else ""
    following = utils.parse._shorten_volume(user["friends_count"])
    followers = utils.parse._shorten_volume(user["followers_count"])
    created_at = user["created_at"]
    created_at_hr = datetime.strptime(created_at,
                                      '%a %b %d %H:%M:%S %z %Y').replace(tzinfo=timezone.utc
                                                                         ).astimezone(tz=None).strftime('%b %Y')

    shorturl = ""
    get_shorturl = " — %s" % exports.get_one("shorturl")(
        event["server"],
        ("https://twitter.com/%s" % profile_username),
        context=event["target"]
    )

    if get_shorturl:
        shorturl = get_shorturl

    return FORMAT_PROFILE_PAGE % (
        utils.irc.bold(profile_username),
        profile_display_name,
        verified,
        utils.irc.bold(created_at_hr),
        utils.irc.bold(total_tweets),
        utils.irc.bold(followers),
        utils.irc.bold(following),
        utils.irc.bold(shorturl)
    )


""" {
    'created_at': 'Sat Jul 25 21:40:42 +0000 2020',
    'id': 1287140748241047554,
    'id_str': '1287140748241047554',
    'full_text': 'Cool Model 3 review by @iamjamiefoxx https://t.co/hJDD7BjkE3',
    'truncated': False,
    'display_text_range': [0,
                           60],
    'entities':
        {
            'hashtags': [],
            'symbols': [],
            'user_mentions':
                [
                    {
                        'screen_name': 'iamjamiefoxx',
                        'name': 'Jamie Foxx',
                        'id': 138600717,
                        'id_str': '138600717',
                        'indices': [23,
                                    36]
                    }
                ],
            'urls':
                [
                    {
                        'url': 'https://t.co/hJDD7BjkE3',
                        'expanded_url': 'https://m.youtube.com/watch?v=tB15Da2TRWw&feature=youtu.be',
                        'display_url': 'm.youtube.com/watch?v=tB15Da…',
                        'indices': [37,
                                    60]
                    }
                ]
        },
    'source': '<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>',
    'in_reply_to_status_id': None,
    'in_reply_to_status_id_str': None,
    'in_reply_to_user_id': None,
    'in_reply_to_user_id_str': None,
    'in_reply_to_screen_name': None,
    'user':
        {
            'id': 44196397,
            'id_str': '44196397',
            'name': 'Elon Musk',
            'screen_name': 'elonmusk',
            'location': '',
            'description': '',
            'url': None,
            'entities': {
                'description': {
                    'urls': []
                }
            },
            'protected': False,
            'followers_count': 37171037,
            'friends_count': 96,
            'listed_count': 54488,
            'created_at': 'Tue Jun 02 20:12:29 +0000 2009',
            'favourites_count': 6194,
            'utc_offset': None,
            'time_zone': None,
            'geo_enabled': False,
            'verified': True,
            'statuses_count': 11777,
            'lang': None,
            'contributors_enabled': False,
            'is_translator': False,
            'is_translation_enabled': False,
            'profile_background_color': 'C0DEED',
            'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme1/bg.png',
            'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme1/bg.png',
            'profile_background_tile': False,
            'profile_image_url': 'http://pbs.twimg.com/profile_images/1276417699032137728/QGSGH8FZ_normal.jpg',
            'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1276417699032137728/QGSGH8FZ_normal.jpg',
            'profile_banner_url': 'https://pbs.twimg.com/profile_banners/44196397/1576183471',
            'profile_link_color': '0084B4',
            'profile_sidebar_border_color': 'C0DEED',
            'profile_sidebar_fill_color': 'DDEEF6',
            'profile_text_color': '333333',
            'profile_use_background_image': True,
            'has_extended_profile': True,
            'default_profile': False,
            'default_profile_image': False,
            'following': True,
            'follow_request_sent': False,
            'notifications': False,
            'translator_type': 'none'
        },
    'geo': None,
    'coordinates': None,
    'place': None,
    'contributors': None,
    'is_quote_status': False,
    'retweet_count': 341,
    'favorite_count': 3718,
    'favorited': False,
    'retweeted': False,
    'possibly_sensitive': False,
    'lang': 'en'
}
 """
