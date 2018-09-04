import uuid
import IRCBuffer

class User(object):
    def __init__(self, nickname, id, server, bot):
        self.set_nickname(nickname)
        self.id = id
        self.username = None
        self.hostname = None
        self.realname = None
        self.server = server
        self.bot = bot
        self.channels = set([])
        self.identified_account = None
        self.buffer = IRCBuffer.Buffer(bot)

    def __repr__(self):
        return "IRCUser.User(%s|%s)" % (self.server.name, self.name)

    def set_nickname(self, nickname):
        self.nickname = nickname
        self.nickname_lower = nickname.lower()
        self.name = self.nickname_lower
    def join_channel(self, channel):
        self.channels.add(channel)
    def part_channel(self, channel):
        self.channels.remove(channel)
    def set_setting(self, setting, value):
        self.bot.database.user_settings.set(self.id, setting, value)
    def get_setting(self, setting, default=None):
        return self.bot.database.user_settings.get(self.id, setting,
            default)
    def find_settings(self, pattern, default=[]):
        return self.bot.database.user_settings.find(self.id, pattern,
            default)
    def find_settings_prefix(self, prefix, default=[]):
        return self.bot.database.user_settings.find_prefix(self.id,
            prefix, default)
    def del_setting(self, setting):
        self.bot.database.user_settings.delete(self.id, setting)
    def get_channel_settings_per_setting(self, setting, default=[]):
        return self.bot.database.user_channel_settings.find_by_setting(
            self.id, setting, default)

    def send_message(self, message, prefix=None):
        self.server.send_message(self.nickname, message, prefix=prefix)
    def send_notice(self, message):
        self.server.send_notice(self.nickname, message)
    def send_ctcp_response(self, command, args):
        self.send_notice("\x01%s %s\x01" % (command, args))
