#--depends-on config
#--depends-on format_activity

import datetime
import os.path

from src import ModuleManager, utils


SETTING = utils.BoolSetting("channel-log", "Enable/disable channel logging")


@utils.export("channelset", utils.BoolSetting("log", "Enable/disable channel logging"))
@utils.export("serverset", SETTING)
@utils.export("botset", SETTING)
class Module(ModuleManager.BaseModule):


    def _enabled(self, server, channel):
        return channel.get_setting("log", server.get_setting("channel-log", self.bot.get_setting("channel-log", False)))


    def _file(self, server_name, channel_name):
        # if a channel name has os.path.sep (e.g. "/") in it, the channel's log
        # file will create a subdirectory.
        #
        # to avoid this, we'll replace os.path.sep with "," (0x2C) as it is
        # forbidden in channel names.
        sanitised_name = channel_name.replace(os.path.sep, ",")
        return self.data_directory("%s/%s.log" % (server_name, sanitised_name))


    def _write_line(self, channel, line):
        #channel._log_file.write("%s\n" % line)
        #channel._log_file.flush()
        #log.debug("%s\n" % line)
        #print("WRITE_LINE")
        #log.info("[%s] %s" % (channel, line))
        return True


    def _write(self, channel, filename, key, line):
        if not hasattr(channel, "_log_file"):
            channel._log_file = utils.io.open(filename, "a")
            channel._log_rsa = None
            channel._log_aes = None

        if key and not key == channel._log_rsa:
            aes_key = utils.security.aes_key()
            channel._log_rsa = key
            channel._log_aes = aes_key

            aes_key_line = utils.security.rsa_encrypt(key, aes_key)
            self._write_line(channel, "\x03%s" % aes_key_line)

        if not channel._log_aes == None:
            line = "\x04%s" % utils.security.aes_encrypt(channel._log_aes, line)
        self._write_line(channel, line)


    def _log(self, server, channel, line):
        if self._enabled(server, channel):
            filename = self._file(str(server), str(channel))
            timestamp = utils.datetime.format.datetime_human(datetime.datetime.now())
            log_line = "%s %s" % (timestamp, line)
            self._write(channel, filename, self.bot.config.get("log-key"), log_line)


    @utils.hook("formatted.message.channel")
    @utils.hook("formatted.notice.channel")
    @utils.hook("formatted.join")
    @utils.hook("formatted.part")
    @utils.hook("formatted.nick")
    @utils.hook("formatted.invite")
    @utils.hook("formatted.mode.channel")
    @utils.hook("formatted.topic")
    @utils.hook("formatted.topic-timestamp")
    @utils.hook("formatted.kick")
    @utils.hook("formatted.quit")
    @utils.hook("formatted.rename")
    @utils.hook("formatted.chghost")
    @utils.hook("formatted.account")
    def on_formatted(self, event):
        #print(event["channel"], event["user"], event["line"], event["server"])
        if event["channel"]:
            self._log(event["server"], event["channel"], event["line"])
        elif event["user"]:
            for channel in event["user"].channels:
                self._log(event["server"], channel, event["line"])
            # log.info("%s - [%s] - %s" % (event["server"].name, channel.name, event["line"].replace("<", "\<")))
