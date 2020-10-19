# --depends-on commands
# --depends-on format_activity
# --depends-on permissions

from src import EventManager, ModuleManager, utils


@utils.export(
    "channelset",
    utils.BoolSetting(
        "relay-extras", "Whether or not to relay joins/parts/quits/modes/etc"
    ),
)
class Module(ModuleManager.BaseModule):
    @utils.hook("new.server")
    def new_server(self, event):
        event["server"]._relay_ignore = []

    def _get_relays(self, channel):
        return channel.get_setting("channel-relays", [])

    def _relay(self, event, channel):
        if (
            "parsed_line" in event
            and event["parsed_line"].id in event["server"]._relay_ignore
        ):
            event["server"]._relay_ignore.remove(event["parsed_line"].id)
            return

        relays = {}
        for relay_group in channel.get_setting("relay-groups", []):
            targets = self.bot.get_setting("relay-group-%s" % relay_group, [])
            for server_id, channel_name in targets:
                server = self.bot.get_server_by_id(server_id)
                if server and channel_name in server.channels:
                    relay_channel = server.channels.get(channel_name)
                    if not channel.id == relay_channel.id:
                        if not server in relays:
                            relays[server] = []
                        if not relay_channel in relays[server]:
                            relays[server].append(relay_channel)

        for server in relays.keys():
            for relay_channel in relays[server]:
                relay_prefix_channel = ""
                if not relay_channel.name == channel.name:
                    relay_prefix_channel = channel.name

                server_name = utils.irc.color(
                    str(event["server"]), utils.consts.LIGHTBLUE
                )
                server_name = "%s%s" % (server_name, utils.consts.RESET)
                relay_message = "[%s%s] %s" % (
                    server_name,
                    relay_prefix_channel,
                    event["minimal"],
                )

                self.bot.trigger(
                    self._send_factory(server, relay_channel.name, relay_message)
                )

    def _send_factory(self, server, channel_name, message):
        def _():
            line = server.send_message(channel_name, message)
            server._relay_ignore.append(line.parsed_line.id)

        return _

    @utils.hook("formatted.message.channel")
    @utils.hook("formatted.notice.channel")
    @utils.kwarg("priority", EventManager.PRIORITY_LOW)
    def formatted(self, event):
        self._relay(event, event["channel"])

    @utils.hook("formatted.join")
    @utils.hook("formatted.part")
    @utils.hook("formatted.nick")
    @utils.hook("formatted.mode.channel")
    @utils.hook("formatted.kick")
    @utils.hook("formatted.quit")
    @utils.hook("formatted.rename")
    @utils.kwarg("priority", EventManager.PRIORITY_LOW)
    def formatted_extra(self, event):
        if event["channel"]:
            if event["channel"].get_setting("relay-extras", False):
                self._relay(event, event["channel"])
        elif event["user"]:
            for channel in event["user"].channels:
                if channel.get_setting("relay-extras", False):
                    self._relay(event, channel)

    @utils.hook("received.command.relaygroup")
    @utils.kwarg("help", "Edit configured relay groups")
    @utils.kwarg("permission", "relay")
    @utils.spec("!'list")
    @utils.spec("!'join,leave !<name>wordlower")
    def relay_group(self, event):
        group_settings = self.bot.find_settings(prefix="relay-group-")
        groups = {}
        for setting, value in group_settings:
            name = setting.replace("relay-group-", "", 1)
            groups[name] = value

        if event["spec"][0] == "list":
            event["stdout"].write("Relay groups: %s" % ", ".join(groups.keys()))
            return

        name = event["spec"][1]

        event["check_assert"](utils.Check("is-channel"))
        current_channel = [event["server"].id, event["target"].name]
        channel_groups = event["target"].get_setting("relay-groups", [])

        message = None
        remove = False

        if event["spec"][0] == "join":
            if not name in groups:
                groups[name] = []

            if current_channel in groups[name] or name in channel_groups:
                raise utils.EventError("Already joined group '%s'" % name)

            groups[name].append(current_channel)
            channel_groups.append(name)
            message = "Joined"

        elif event["spec"][0] == "leave":
            if (
                not name in groups
                or not current_channel in groups[name]
                or not name in channel_groups
            ):
                raise utils.EventError("Not in group '%s'" % name)

            groups[name].remove(current_channel)
            channel_groups.remove(name)
            message = "Left"

        if not message == None:
            if not groups[name]:
                self.bot.del_setting("relay-group-%s" % name)
            else:
                self.bot.set_setting("relay-group-%s" % name, groups[name])

            if channel_groups:
                event["target"].set_setting("relay-groups", channel_groups)
            else:
                event["target"].del_setting("relay-groups")

            event["stdout"].write("%s group '%s'" % (message, name))
