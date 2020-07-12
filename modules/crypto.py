#--depends-on commands

import hashlib, re, urllib.parse, datetime, time
from src import EventManager, ModuleManager, utils

TICKER_URL = "https://blockchain.info/ticker"
STATS_URL = "https://api.blockchain.info/stats"
CONVERT_URL = "https://blockchain.info/tobtc?currency=%s&value=%s"
MIN_TIME = 900


class Module(ModuleManager.BaseModule):
    _valid_currencies = None
    _ticker = None
    _stats = None
    _last_updated = None
    _name = "Bitcoin"

    @utils.hook("received.command.btc", alias_of="bitcoin")
    @utils.hook("received.command.bitcoin", min_args=1)
    @utils.kwarg("help", "Get the current bitcoin value in local currency")
    @utils.kwarg("usage", "<currency code> (ie GBP)")
    def price(self, event):
        self.check_ticker(event)

        currency = event["args"].upper()

        if currency not in self._valid_currencies:
            event["stderr"].write("Invalid currency (%s)" % currency)
            return

        info = self._ticker[currency]
        event["stdout"].write("%s (%s) - %s%s" % (utils.irc.bold("BTC Price"),
                                                  currency,
                                                  utils.irc.bold(info["symbol"]),
                                                  utils.irc.bold(info["last"])))

    @utils.hook("received.command.vc", alias_of="validcurrencies")
    @utils.hook("received.command.validcurrencies")
    @utils.kwarg("help", "Get a list of valid currencies for BTC checking")
    def show_currencies(self, event):
        self.check_ticker(event)

        valid = ", ".join(self._valid_currencies)
        event["stdout"].write("Valid Bitcoin currencies are: %s" % valid)

    @utils.hook("received.command.curtobtc", alias_of="currencytobtc")
    @utils.hook("received.command.currencytobtc", min_args=2)
    @utils.kwarg("help", "Convert currency to BTC amount")
    @utils.kwarg("usage", "<amount> <currency code>")
    def convert(self, event):
        self.check_ticker(event)

        currency = event["args_split"][1].upper()
        amount = event["args_split"][0]
        symbol = self._ticker[currency]["symbol"]

        if currency not in self._valid_currencies:
            event["stderr"].write("Invalid currency (%s)" % currency)
            return

        conv = CONVERT_URL % (currency, amount)
        price = utils.http.request(conv).json()

        event["stdout"].write("Convert %s (%s) to BTC: %s BTC" % (utils.irc.bold(symbol + amount),
                                                                  currency,
                                                                  utils.irc.bold(price)))

    @utils.hook("received.command.btcstats")
    @utils.kwarg("help", "Shows various statistics from the last 24 hours of BTC mining")
    def show_stats(self, event):
        self.check_ticker(event)

        stats = self._stats

        tx = "%s: %s" % (utils.irc.bold("Transactions"), stats["n_tx"])
        blocks_mined = "%s: %s" % (utils.irc.bold("Blocks Mined"), stats["n_blocks_mined"])
        avg_mins = "%s: %s" % (utils.irc.bold("Avg Minutes Between Blocks"), stats["minutes_between_blocks"])
        trade_volume = "%s: %s" % (utils.irc.bold("BTC Traded"), stats["trade_volume_btc"])

        title = "%s (Last 24 Hours)" % utils.irc.bold("BTC Stats")

        event["stdout"].write("%s: %s — %s — %s — %s" % (title, tx, blocks_mined, avg_mins, trade_volume))

    def check_ticker(self, event):
        if self._ticker == None or self._valid_currencies == None or self._last_updated == None:
            self.populate_ticker()

        if self._last_updated != None:
            time_now = round(time.time())
            if (time_now - self._last_updated) > MIN_TIME:
                self.populate_ticker()

    def populate_ticker(self):
        ticker = utils.http.request(TICKER_URL).json()
        stats = utils.http.request(STATS_URL).json()

        if self._valid_currencies == None:
            valid = []
            for cur in ticker:
                valid.append(cur)

            self._valid_currencies = valid

        self._ticker = ticker
        self._stats = stats
        self._last_updated = round(time.time())
