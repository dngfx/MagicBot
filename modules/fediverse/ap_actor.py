import email.utils, urllib.parse
from src import utils
from . import ap_security, ap_utils

<<<<<<< HEAD

class Actor(object):

=======
class Actor(object):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def __init__(self, url):
        self.url = url

        self.username = None
        self.display_name = None
        self.inbox = None
        self.outbox = None
        self.followers = None

    def load(self):
        response = ap_utils.activity_request(self.url)
        if response.code == 200:
            response = response.json()
            self.username = response["preferredUsername"]
            self.display_name = response.get("name") or self.username
            self.inbox = Inbox(response["inbox"])
            self.outbox = Outbox(response["outbox"])
            self.followers = response["followers"]
            return True
        return False

<<<<<<< HEAD

class Outbox(object):

=======
class Outbox(object):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def __init__(self, url):
        self._url = url

    def load(self):
        outbox = ap_utils.activity_request(self._url).json()

        items = None
        if "first" in outbox:
            if type(outbox["first"]) == dict:
                # pleroma
                items = outbox["first"]["orderedItems"]
            else:
                # mastodon
                first = ap_utils.activity_request(outbox["first"]).json()
                items = first["orderedItems"]
        else:
            items = outbox["orderedItems"]
        return items

<<<<<<< HEAD

class Inbox(object):

    def __init__(self, url):
        self._url = url

    def send(self, sender, activity, private_key):
        now = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
        parts = urllib.parse.urlparse(self._url)
        headers = [["Host", parts.netloc], ["Date", now]]
=======
class Inbox(object):
    def __init__(self, url):
        self._url = url
    def send(self, sender, activity, private_key):
        now = email.utils.formatdate(timeval=None, localtime=False, usegmt=True)
        parts = urllib.parse.urlparse(self._url)
        headers = [
            ["Host", parts.netloc],
            ["Date", now]
        ]
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
        sign_headers = headers[:]
        sign_headers.insert(0, ["(request-target)", "post %s" % parts.path])
        signature = ap_security.signature(private_key, sign_headers)

        headers.append(["signature", signature])

<<<<<<< HEAD
        return ap_utils.activity_request(self._url,
                                         activity.format(sender),
                                         method="POST",
                                         headers=dict(headers)).json()
=======
        return ap_utils.activity_request(self._url, activity.format(sender),
            method="POST", headers=dict(headers)).json()

>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
