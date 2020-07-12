#--depends-on commands
#--depends-on config
#--depends-on permissions

import time, math
from src import EventManager, ModuleManager, utils


class Module(ModuleManager.BaseModule):

    def _user_all(self, user):
        return self.bot.database.execute_fetchall("SELECT channel_id, count FROM words WHERE user_id=?",
                                                  [user.get_id()])

    @utils.hook("received.command.xp", channel_only=True)
    @utils.kwarg("help", "See your XP score!")
    @utils.spec("!-channelonly ?<nickname>ouser")
    def words(self, event):
        target_user = event["spec"][0] or event["user"]

        words = dict(self._user_all(target_user))
        this_channel = words.get(event["target"].id, 0)

        total = 0
        for channel_id in words:
            total += words[channel_id]

        rounded = (total * round(total * 0.0003))
        calc = rounded if rounded > 100 else total
        level = math.ceil(calc / 500)
        
        event["stdout"].write("%s has %s XP. They are level %s" % (target_user.nickname, calc, level))
