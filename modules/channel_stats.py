# --depends-on commands
# --depends-on config
# --depends-on permissions

from src import ModuleManager, utils


@utils.export(
    "channelset",
    utils.BoolSetting(
        "announce-new-peak-users",
        "Whether or not to announce when a new user peak is reached!",
    ),
)
class Module(ModuleManager.BaseModule):
    _name = "ChanStats"

    def _parse_peak_users(self, channel):
        current_users = channel.user_count()
        peak_users = channel.get_setting("peak-users", 0)

        if current_users > peak_users:
            channel.set_setting("peak-users", current_users)
            return [True, current_users]
        else:
            return [False, current_users]

    def _get_wordcount(self, channel):
        return self.bot.database.execute_fetchall(
            "SELECT user_id, SUM(count) as total FROM words WHERE channel_id=? AND user_id != 3 GROUP BY user_id ORDER BY total DESC LIMIT 2",
            [channel.id],
        )

    def _get_nick_from_id(self, user_id, server_id):
        return self.bot.database.execute_fetchone(
            "SELECT nickname FROM users WHERE user_id=? AND server_id=?",
            [user_id, server_id],
        )[0]

    @utils.hook("new.channel")
    def new_channel(self, event):
        self._parse_peak_users(event["channel"])
        return True

    @utils.hook("received.join")
    def on_join(self, event):
        channel = event["channel"]
        user = event["user"]
        new_peak = self._parse_peak_users(channel)
        if (
            channel.get_setting("announce-new-peak-users", False)
            and new_peak[0] != False
        ):
            channel.send_message(
                "A new user peak has been reached! New peak: %s"
                % utils.irc.bold(str(new_peak[1]))
            )

    @utils.hook("received.command.chanstats", channel_only=True)
    @utils.kwarg("help", "See the current channel stats")
    def channel_stats(self, event):
        channel = event["target"]
        server = event["server"]
        server_id = server.id

        self._parse_peak_users(channel)

        current_users = channel.user_count()
        peak_users = channel.get_setting("peak-users", 0)

        wordcount = self._get_wordcount(channel)
        print(wordcount)
        wordiest_id, wordiest_count = wordcount[0]
        runnerup_id, runnerup_count = wordcount[1]

        wordiest_count = utils.parse.comma_format(wordiest_count)
        runnerup_count = utils.parse.comma_format(runnerup_count)

        wordiest_nick = self._get_nick_from_id(wordiest_id, server_id)
        runnerup_nick = self._get_nick_from_id(runnerup_id, server_id)

        event["stdout"].write(
            "Stats for %s: Users (Current: %s, Peak: %s) — Wordiest User (%s with %s words) — Second Place (%s with %s words)"
            % (
                utils.irc.bold(channel.name),
                utils.irc.bold(current_users),
                utils.irc.bold(peak_users),
                utils.irc.bold(utils.prevent_highlight(wordiest_nick)),
                utils.irc.bold(wordiest_count),
                utils.irc.bold(utils.prevent_highlight(runnerup_nick)),
                utils.irc.bold(runnerup_count),
            )
        )
