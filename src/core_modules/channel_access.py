#--depends-on check_mode
#--depends-on commands
#--depends-on permissions

from src import ModuleManager, utils

SPECIAL = ["low", "high", "admin"]


class Module(ModuleManager.BaseModule):
    _name = "ChanAccess"

    def _has_channel_access(self, target, user, names):
        required_access = []
        for name in names.split(","):
            name = name.strip()

            if name in SPECIAL:
                required_access.extend(SPECIAL[:SPECIAL.index(name) + 1])
            else:
                required_access.append(name)

        user_access = target.get_user_setting(user.get_id(), "access", [])
        identified = self.exports.get_one("is-identified")(user)
        matched = list(set(required_access) & set(user_access))

        return ("*" in user_access or matched) and identified

    def _command_check(self, event, channel, require_access):
        if channel:
            if self._has_channel_access(channel, event["user"], require_access):
                return utils.consts.PERMISSION_FORCE_SUCCESS, None
            else:
                return (utils.consts.PERMISSION_ERROR, "You do not have permission to do this")
        else:
            raise ValueError("_command_check requires a channel")

    @utils.hook("preprocess.command")
    def preprocess_command(self, event):
        require_access = event["hook"].get_kwarg("require_access")
        if require_access:
            channel = event["kwargs"].get("channel", event["target"] if event["is_channel"] else None)
            return self._command_check(event, channel, require_access)

    @utils.hook("check.command.channel-access")
    def check_command(self, event):
        target = event["target"]
        access = event["request_args"][0]
        if len(event["request_args"]) > 1:
            target = event["request_args"][0]
            access = event["request_args"][1]

        return self._command_check(event, target, access)

    @utils.hook("received.command.access")
    @utils.kwarg("require_mode", "high")
    @utils.spec("!<#channel>r~channel !'list !<nickname>ouser")
    @utils.spec("!<#channel>r~channel !'add,remove,set !<nickname>ouser " "!<permissions>string")
    def access(self, event):
        channel = event["spec"][0]
        subcommand = event["spec"][1].lower()
        target = event["spec"][2]
        access = channel.get_user_setting(target.get_id(), "access", [])

        if subcommand == "list":
            event["stdout"].write("Access for %s: %s" % (target.nickname, " ".join(access)))
        elif subcommand == "set":
            channel.set_user_setting(target.get_id(), "access", event["spec"][3])
        elif subcommand == "add":
            for acc in event["spec"][3].split(" "):
                if acc in access:
                    raise utils.EventError("%s already has '%s' permission" % (target.nickname, acc))
                access.append(acc)
            channel.set_user_setting(target.get_id(), "access", access)
            event["stdout"].write("Added permission to %s: %s" % (target.nickname, event["spec"][3]))
        elif subcommand == "remove":
            for acc in event["spec"][3].split(" "):
                if not acc in access:
                    raise utils.EventError("%s does not have '%s' permission" % (target.nickname, acc))
                access.remove(acc)
            if access:
                channel.set_user_setting(target.get_id(), "access", access)
            else:
                channel.del_user_setting(target.get_id(), "access")
            event["stdout"].write("Removed permission from %s: %s" % (target.nickname, event["spec"][3]))
        else:
            event["stderr"].write("Unknown command '%s'" % subcommand)
