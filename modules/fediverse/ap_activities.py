from . import utils as ap_utils

<<<<<<< HEAD

class Activity(object):
    _type = ""

    def __init__(self, id, object):
        self._id = id
        self._object = object

=======
class Activity(object):
    _type = ""
    def __init__(self, id, object):
        self._id = id
        self._object = object
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    def format(self, actor):
        return {
            "@context": "https://www.w3.org/ns/activitystreams",
            "actor": actor.url,
            "id": self._id,
            "object": self._object,
            "type": self._type
        }

<<<<<<< HEAD

class Follow(Activity):
    _type = "Follow"


class Accept(Activity):
    _type = "Accept"


class Create(Activity):
    _type = "Create"


=======
class Follow(Activity):
    _type = "Follow"
class Accept(Activity):
    _type = "Accept"

class Create(Activity):
    _type = "Create"

>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
class Announce(Activity):
    _type = "Announce"
