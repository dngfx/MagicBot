# --depends-on commands
# --depends-on permissions

import sys
import pprint

from src import IRCBot, IRCLine, ModuleManager, utils, Config
from src.Logging import Logger as log


class Module(ModuleManager.BaseModule):
    @utils.hook("received.command.nick")
    @utils.kwarg("help", "Change my nickname")
    @utils.kwarg("permission", "changenickname")
    @utils.spec("!<nickname>word")
    def change_nickname(self, event):
        event["server"].send_nick(event["spec"][0])

    @utils.hook("received.command.broadcast")
    @utils.kwarg("help", "Send a message to every channel on the current server")
    @utils.kwarg("permission", "administrator")
    @utils.spec("!<message>string")
    def broadcast_message(self, event):
        broadcast_text = event["spec"][0]
        server = event["server"]
        message = 'Broadcasting "%s" to all channels on %s' % (
            utils.irc.bold(broadcast_text),
            utils.irc.bold(server.alias),
        )
        event["stdout"].write(message)
        for channel in server.get_channels():
            chan = channel[0]
            server.send_message(chan, broadcast_text)

    @utils.hook("received.command.raw")
    @utils.kwarg("help", "Send a line of raw IRC data")
    @utils.kwarg("permission", "raw")
    @utils.spec("!<line>string")
    def raw(self, event):
        if IRCLine.is_human(event["spec"][0]):
            line = IRCLine.parse_human(event["spec"][0])
        else:
            line = IRCLine.parse_line(event["spec"][0])
        line = event["server"].send(line)

        if not line == None:
            event["stdout"].write("Sent: %s" % line.parsed_line.format())
        else:
            event["stderr"].write("Line was filtered")

    @utils.hook("received.command.part")
    @utils.kwarg("help", "Part from the current or given channel")
    @utils.kwarg("permission", "part")
    @utils.spec("!r~channel")
    def part(self, event):
        event["server"].send_part(event["spec"][0].name)

    @utils.hook("received.command.rehashconfig")
    @utils.hook("received.command.rehashcfg")
    @utils.kwarg("help", "Reloads the config file of the bot")
    @utils.kwarg("permission", "rehash-config")
    def rehash(self, event):
        # idek

        log.info("Now Rehashing Bot Config")
        config = self.bot.get_config("bot")

        config_array = vars(config)["_config"].items()
        for item, value in config_array:
            self.bot.config[item] = value

        log.success("Config updated!", formatting=True)
        event["stdout"].write("Config file successfully reloaded!")

    def _id_from_alias(self, alias):
        return self.bot.database.servers.get_by_alias(alias)

    def _server_from_alias(self, alias):
        id, server = self._both_from_alias(alias)
        return server

    def _both_from_alias(self, alias):
        id = self._id_from_alias(alias)
        if id == None:
            raise utils.EventError("Unknown server alias")
        return id, self.bot.get_server_by_id(id)

    @utils.hook("received.command.reconnect")
    @utils.kwarg("help", "Reconnect to the current, or provided, server")
    @utils.kwarg("permission", "reconnect")
    @utils.spec("?<server>word")
    def reconnect(self, event):
        alias = event["spec"][0] or str(event["server"])
        server = self._server_from_alias(alias)

        if server:
            line = server.send_quit("Reconnecting")
            line.events.on("send").hook(
                lambda e: self.bot.reconnect(
                    server.id, server.connection_params)
            )
            if not server == event["server"]:
                event["stdout"].write("Reconnecting to %s" % alias)
        else:
            event["stdout"].write("Not connected to %s" % alias)

    @utils.hook("received.command.connect", min_args=1)
    @utils.kwarg("help", "Connect to a given server")
    @utils.kwarg("permission", "connect")
    @utils.spec("!<server>word")
    def connect(self, event):
        alias = event["spec"][0]
        server = self._server_from_alias(alias)
        if server:
            raise utils.EventError("Already connected to %s" % str(server))

        server = self.bot.add_server(self._id_from_alias(alias))
        event["stdout"].write("Connecting to %s" % str(server))

    @utils.hook("received.command.disconnect")
    @utils.kwarg("help", "Disconnect from the current or provided server")
    @utils.kwarg("permission", "disconnect")
    @utils.spec("?<server>word")
    def disconnect(self, event):
        alias = event["spec"][0] or str(event["server"])
        id, server = self._both_from_alias(alias)

        if not server == None:
            server.disconnect()
            self.bot.disconnect(server)
        elif id in self.bot.reconnections:
            self.bot.reconnections[id].cancel()
            del self.bot.reconnections[id]
        else:
            raise utils.EventError("Server not connected")

        if not server == event["server"]:
            event["stdout"].write("Disconnected from %s" % alias)

    @utils.hook("received.command.shutdown")
    @utils.kwarg("help", "Shutdown the bot")
    @utils.kwarg("permission", "shutdown")
    @utils.spec("?<reason>string")
    def shutdown(self, event):
        reason = event["spec"][0] if event["spec"][0] else "Shutting down"
        for server in self.bot.servers.values():
            line = server.send_quit(reason)
            line.events.on("send").hook(self._shutdown_hook(server))

        self.quit_process()

    def quit_process(self):
        sys.exit()

    def _shutdown_hook(self, server):
        def shutdown(e):
            server.disconnect()
            self.bot.disconnect(server)

        return shutdown

    @utils.hook("received.command.addserver")
    @utils.kwarg("help", "Add a new server")
    @utils.kwarg("pemission", "addserver")
    @utils.spec("!<alias>word !<hostname:port>word !<nickname!username@bindhost>word")
    def add_server(self, event):
        alias = event["spec"][0]
        hostname, sep, port = event["spec"][1].partition(":")
        tls = port.startswith("+")
        port = port.lstrip("+")

        if not hostname or not port or not port.isdigit():
            raise utils.EventError("Please provide <hostname>:[+]<port>")
        port = int(port)

        hostmask = IRCLine.parse_hostmask(event["spec"][2])
        nickname = hostmask.nickname
        username = hostmask.username or nickname
        realname = nickname
        bindhost = hostmask.hostname or None

        try:
            server_id = self.bot.database.servers.add(
                alias, hostname, port, "", tls, bindhost, nickname, username, realname
            )
        except Exception as e:
            event["stderr"].write("Failed to add server")
            log.error('failed to add server "%s"', [alias], exc_info=True)
            return
        event["stdout"].write("Added server '%s'" % alias)

    @utils.hook("received.command.editserver")
    @utils.kwarg("help", "Edit server details")
    @utils.kwarg("permission", "editserver")
    @utils.spec("!<alias>word !<option>word !<value>string")
    def edit_server(self, event):
        alias = event["spec"][0]
        server_id = self._id_from_alias(alias)
        if server_id == None:
            raise utils.EventError("Unknown server '%s'" % alias)

        option = event["spec"][1].lower()
        value = event["spec"][2]
        value_parsed = None

        if option == "hostname":
            value_parsed = value
        elif option == "port":
            if not value.isdigit():
                raise utils.EventError("Invalid port")
            value_parsed = int(value.lstrip("0"))
        elif option == "tls":
            value_lower = value.lower()
            if not value_lower in ["yes", "no"]:
                raise utils.EventError("TLS should be either 'yes' or 'no'")
            value_parsed = value_lower == "yes"
        elif option == "password":
            value_parsed = value
        elif option == "bindhost":
            value_parsed = value
        elif option in ["nickname", "username", "realname"]:
            value_parsed = value
        else:
            raise utils.EventError("Unknown option '%s'" % option)

        self.bot.database.servers.edit(server_id, option, value_parsed)
        event["stdout"].write("Set %s for %s" % (option, alias))
