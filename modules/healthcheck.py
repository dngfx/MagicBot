# --require-config healthcheck-url

from src import ModuleManager, utils
from src.Logging import Logger as log


# this module was created for use with https://healthchecks.io/
# but it can be used for any similar URL-pinging service.


class Module(ModuleManager.BaseModule):
    @utils.hook("cron")
    @utils.kwarg("schedule", "*/10")
    def ten_minutes(self, event):
        url = self.bot.config["healthcheck-url"]
        try:
            utils.http.request(url)
        except Exception as e:
            log.error(
                "Failed to call healthcheck-url (%s)" % url, "Internal", "healthcheck"
            )
