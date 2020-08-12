#--depends-on commands
#--depends-on permissions

import time

from src import EventManager, ModuleManager, utils


SILENCE_TIME = 60 * 5  # 5 minutes


class Module(ModuleManager.BaseModule):


    def _is_silenced(self, target):
        silence_until = target.get_setting("silence-until", None)
        if not silence_until == None:
            if time.time() < silence_until:
                return True
            else:
                target.del_setting("silence-until")
        return False


    @utils.hook("received.command.silence")
    @utils.kwarg("help", "Prevent me saying anything for a period of time " "(default: 5 minutes)")
    @utils.kwarg("require_mode", "high")
    @utils.kwarg("require_access", "low,silence")
    @utils.kwarg("permission", "silence")
    @utils.spec("!-channelonly ?duration")
    def silence(self, event):
        duration = event["spec"][0] or SILENCE_TIME
        silence_until = time.time() + duration
        event["target"].set_setting("silence-until", silence_until)
        event["stdout"].write("Ok, I'll be back")


    @utils.hook("received.command.unsilence")
    @utils.kwarg("help", "Unsilence me")
    @utils.kwarg("unsilence", True)
    @utils.kwarg("channel_only", True)
    @utils.kwarg("require_mode", "high")
    @utils.kwarg("require_access", "low,unsilence")
    @utils.kwarg("permission", "unsilence")
    def unsiltence(self, event):
        silence_until = event["target"].get_setting("silence-until", None)
        if not silence_until == None:
            event["target"].del_setting("silence-until")
            event["stdout"].write("Ok. I've been unsilenced")
        else:
            event["stderr"].write("I am not silenced")


    @utils.hook("preprocess.command", priority=EventManager.PRIORITY_HIGH)
    def preprocess_command(self, event):
        if event["is_channel"] and not event["hook"].get_kwarg("unsilence", False):
            silence_until = event["target"].get_setting("silence-until", None)
            if silence_until:
                if self._is_silenced(event["target"]):
                    return utils.consts.PERMISSION_HARD_FAIL, None


    @utils.hook("unknown.command")
    @utils.kwarg("priority", EventManager.PRIORITY_HIGH)
    def unknown_command(self, event):
        if event["is_channel"] and self._is_silenced(event["target"]):
            event.eat()
