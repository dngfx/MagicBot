# --depends-on commands
# --depends-on format_activity

import time

from src import ModuleManager, utils


class Module(ModuleManager.BaseModule):
    def _change_seen(self, channel, user, action):
        user.set_setting("seen", time.time())
        channel.set_user_setting(
            user.get_id(), "seen-info", {"action": action})

    @utils.hook("formatted.message.channel")
    @utils.hook("formatted.notice.channel")
    def on_formatted(self, event):
        line = event["minimal"] or event["line"]

        if not event["server"].is_own_nickname(event["user"].nickname):
            self._change_seen(event["channel"], event["user"], line)

    @utils.hook("received.command.seen")
    @utils.kwarg("help", "Find out when a user was last seen")
    @utils.spec("!<nickname>ouser")
    def seen(self, event):
        user = event["spec"][0]
        seen_seconds = user.get_setting("seen") or None
        seen_info = ""

        if seen_seconds:
            seen_info = None
            if event["is_channel"]:
                seen_info = event["target"].get_user_setting(
                    user.get_id(), "seen-info", None
                )
                if seen_info:
                    seen_info = " (%s%s)" % (
                        seen_info["action"], utils.consts.RESET)
                else:
                    seen_info = ""
            since = utils.datetime.format.to_pretty_since(
                time.time() - seen_seconds, max_units=2
            )
            event["stdout"].write(
                "%s was last seen %s ago%s"
                % (event["args_split"][0], since, seen_info or "")
            )
        else:
            event["stderr"].write(
                "I have never seen %s before." % (event["args_split"][0])
            )
