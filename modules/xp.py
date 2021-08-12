# --depends-on commands
# --depends-on config
# --depends-on permissions

from src import ModuleManager, utils


@utils.export("channelset", utils.BoolSetting("xp-enabled", "Is the XP module enabled?"))
class Module(ModuleManager.BaseModule):

    def _user_all(self, user):
        return self.bot.database.execute_fetchall("SELECT channel_id, count FROM words WHERE user_id=?",
                                                  [user.get_id()])

    def _get_user_info_from_id(self, id):
        return self.bot.database.execute_fetchone("SELECT server_id, nickname FROM users WHERE user_id=?", [id])

    def _get_server_from_id(self, id):
        return self.bot.get_server_by_id(id)

    def _getLevel(self, points):
        levels = [0, 250, 500, 750, 1000, 1250, 1500, 1750, 2000, 2500, 3000,
                  5000, 7500, 10000, 15000, 20000, 30000, 50000, 100000, 250000]
        lvl = len([x for x in levels if points > x])
        return lvl

    @utils.hook("received.command.xp", channel_only=True)
    @utils.kwarg("help", "See your XP score!")
    @utils.spec("!-channelonly ?<nickname>ouser")
    def get_xp(self, event):
        channel = event["channel"]
        target_user = event["spec"][0] or event["user"]
        nick = target_user.nickname
        user_id = target_user.get_id()
        setting = "xp-%s" % nick
        cur_xp = channel.get_user_setting(user_id, setting, 0)
        level = self._getLevel(cur_xp)
        level = 1 if level == 0 else level

        event["stdout"].write("%s has %s XP. They're level %s" % (
            nick, cur_xp, utils.irc.bold(str(level))))

    @utils.hook("received.command.xpaddinternal")
    @utils.kwarg("help", "See your XP score!")
    @utils.export("xpaddinternal")
    def add_xp_internal(self, info):
        parts = info.split(":")

        user_id = int(parts[0])
        channel_id = parts[1]
        channel_name = parts[2]
        xp = int(parts[3])

        server_id, nick = self._get_user_info_from_id(user_id)
        server = self._get_server_from_id(server_id)
        channel = server.channels.get(channel_name)

        setting = "xp-%s" % nick

        cur_xp = channel.get_user_setting(user_id, setting, 0)
        xp += cur_xp
        channel.set_user_setting(user_id, setting, xp)

        return [cur_xp, xp]
