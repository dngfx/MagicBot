import collections

<<<<<<< HEAD

class DNSBL(object):

=======
class DNSBL(object):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def __init__(self, hostname=None):
        if not hostname == None:
            self.hostname = hostname

    def process(self, result: str):
        return "unknown"

<<<<<<< HEAD

class ZenSpamhaus(DNSBL):
    hostname = "zen.spamhaus.org"

=======
class ZenSpamhaus(DNSBL):
    hostname = "zen.spamhaus.org"
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def process(self, result):
        result = result.rsplit(".", 1)[1]
        if result in ["2", "3", "9"]:
            return "spam"
        elif result in ["4", "5", "6", "7"]:
            return "exploits"
<<<<<<< HEAD


class EFNetRBL(DNSBL):
    hostname = "rbl.efnetrbl.org"

=======
class EFNetRBL(DNSBL):
    hostname = "rbl.efnetrbl.org"
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def process(self, result):
        result = result.rsplit(".", 1)[1]
        if result == "1":
            return "proxy"
        elif result in ["2", "3"]:
            return "spamtap"
        elif result == "4":
            return "tor"
        elif result == "5":
            return "flooding"

<<<<<<< HEAD

class DroneBL(DNSBL):
    hostname = "dnsbl.dronebl.org"

=======
class DroneBL(DNSBL):
    hostname = "dnsbl.dronebl.org"
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def process(self, result):
        result = result.rsplit(".", 1)[1]
        if result in ["8", "9", "10", "11", "14"]:
            return "proxy"
        elif result in ["3", "6", "7"]:
            return "flooding"
        elif result in ["12", "13", "15", "16"]:
            return "exploits"

<<<<<<< HEAD

DEFAULT_LISTS = [ZenSpamhaus(), EFNetRBL(), DroneBL()]


def default_lists():
    return collections.OrderedDict((dnsbl.hostname, dnsbl) for dnsbl in DEFAULT_LISTS)
=======
DEFAULT_LISTS = [
    ZenSpamhaus(),
    EFNetRBL(),
    DroneBL()
]

def default_lists():
    return collections.OrderedDict(
        (dnsbl.hostname, dnsbl) for dnsbl in DEFAULT_LISTS)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
