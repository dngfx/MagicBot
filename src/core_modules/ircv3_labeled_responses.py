import uuid

from src import EventManager, ModuleManager, utils


CAP = utils.irc.Capability("labeled-response", "draft/labeled-response-0.2", depends_on=["batch"])
TAG = utils.irc.MessageTag("label", "draft/label")
BATCH = utils.irc.BatchType("labeled-response", "draft/labeled-response")

CAP_TO_TAG = {
    "draft/labeled-response-0.2": "draft/label",
    "labeled-response":           "label"
}


class WaitingForLabel(object):


    def __init__(self, line, events):
        self.line = line
        self.events = events
        self.labels_since = 0


@utils.export("cap", CAP)
class Module(ModuleManager.BaseModule):


    @utils.hook("new.server")
    def new_server(self, event):
        event["server"]._label_cache = {}


    @utils.hook("preprocess.send")
    def raw_send(self, event):
        available_cap = event["server"].available_capability(CAP)

        if available_cap:
            label = TAG.get_value(event["line"].tags)
            if label == None:
                tag_key = CAP_TO_TAG[available_cap]
                label = str(uuid.uuid4())
                event["line"].tags[tag_key] = label

            event["server"]._label_cache[label] = WaitingForLabel(event["line"], event["events"])


    @utils.hook("raw.received")
    @utils.kwarg("priority", EventManager.PRIORITY_HIGH)
    def raw_recv(self, event):
        if not event["line"].command == "BATCH":
            label = TAG.get_value(event["line"].tags)
            if not label == None:
                self._recv(event["server"], label, [event["line"]])


    @utils.hook("received.batch.end")
    def batch_end(self, event):
        if BATCH.match(event["batch"].type):
            label = TAG.get_value(event["batch"].tags)
            self._recv(event["server"], label, event["batch"].get_lines())


    def _recv(self, server, label, lines):
        if not label in server._label_cache:
            log.debug(message=("unknown label received on %s: %s" % (str(server), label)), server=str(server), context="IRCv3", formatting=True)
            return

        cached = server._label_cache.pop(label)
        cached.events.on("labeled-response").call(line=cached.line, responses=lines, server=server)

        for label, other_cached in server._label_cache.items():
            other_cached.labels_since += 1
            if other_cached.labels_since == 10:
                log.debug(message=("%d labels seen while waiting for response to %s on %s" % (other_cached.labels_since,
                                label,
                                str(server))), server=str(server), context="IRCv3", formatting=True)
