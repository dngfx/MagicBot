# --depends-on commands

from src import ModuleManager, utils


API_URL = "https://api.coincap.io/v2/%s"
MIN_TIME = 900
ARROW_UP = "↑"
ARROW_DOWN = "↓"


class Module(ModuleManager.BaseModule):
    _assets = {}
    _name = "Cryptocurrency"

    @utils.hook("received.command.coinstats")
    @utils.kwarg("help", "Shows market information about the coin requested")
    @utils.spec("!<coin>word")
    def show_stats(self, event):
        coin = event["spec"][0].upper()
        page = utils.http.request(
            (API_URL % "assets"), get_params={"search": coin, "limit": 1}
        ).json()
        data = page["data"]

        if not data:
            event["stderr"].write("Invalid Coin (%s)" % utils.irc.bold(coin))
            return

        info = data[0]

        self._assets[info["symbol"]] = info

        # Bitcoin (BTC) Last 24H — Trade Vol: $2.6B — Avg Price: $9257.11 — Chg -0.18%
        # —=

        trade_vol = str(info["volumeUsd24Hr"].split(".")[0])
        trade_vol_formatted = utils.parse.shorten_volume(trade_vol)

        chg_parts = info["changePercent24Hr"].split(".")
        chg_positive = float(info["changePercent24Hr"]) > 0
        chg = "%s.%s" % (chg_parts[0], chg_parts[1][:3])
        color = utils.consts.GREEN if chg_positive else utils.consts.RED
        arrow = ARROW_UP if chg_positive else ARROW_DOWN
        chg_text = utils.irc.bold(utils.irc.color(chg + "% " + arrow, color))
        avg_parts = info["vwap24Hr"].split(".")
        avg_price = "%s.%s" % (utils.parse.comma_format(
            avg_parts[0]), avg_parts[1][:2])

        event["stdout"].write(
            "%s (%s) Last 24H — Trade Vol: %s — Avg Price: %s — Chg: %s"
            % (
                info["name"],
                utils.irc.bold(info["symbol"]),
                utils.irc.bold("$" + trade_vol_formatted),
                utils.irc.bold("$" + avg_price),
                chg_text,
            )
        )

    @utils.hook("received.command.curtocoin", alias_of="currencytocoin")
    @utils.hook("received.command.currencytocoin")
    @utils.kwarg("help", "Convert currency to coin amount")
    @utils.spec("!<amount>word !<currency>word !<coin>word")
    def convert(self, event):
        currency = event["spec"][1].upper()
        amount = event["spec"][0]
        coin = event["spec"][2].upper()

        page = utils.http.request(
            API_URL % "markets",
            get_params={"baseSymbol": coin,
                        "quoteSymbol": currency, "limit": 1},
        ).json()
        data = page["data"]

        if not data:
            event["stderr"].write(
                "Invalid Cryptocurrency (%s)" % utils.irc.bold(coin))
            return

        info = data[0]
        price = str(int(amount) / int(info["priceQuote"].split(".")[0]))[:8]
        # symbol = info["quoteSymbol"]

        event["stdout"].write(
            "Convert %s %s to %s: %s %s"
            % (
                utils.irc.bold(amount),
                utils.irc.bold(currency),
                utils.irc.bold(coin),
                utils.irc.bold(price),
                utils.irc.bold(coin),
            )
        )

    @utils.hook("received.command.coinprice")
    @utils.kwarg("help", "Get the price of one coin in local currency")
    @utils.spec("!<coin>word !<currency>word")
    def onecoin(self, event):
        currency = event["spec"][1].upper()
        coin = event["spec"][0].upper()

        page = utils.http.request(
            API_URL % "markets",
            get_params={"baseSymbol": coin,
                        "quoteSymbol": currency, "limit": 1},
        ).json()
        data = page["data"]

        if not data:
            event["stderr"].write(
                "Invalid Cryptocurrency or no marketplace is willing to trade that currency pair"
            )
            return

        info = data[0]
        price_parts = info["priceQuote"].split(".")
        price = "%s.%s" % (utils.parse.comma_format_number(
            price_parts[0]), price_parts[1][:2])
        # symbol = info["quoteSymbol"]

        event["stdout"].write(
            "%s to %s: 1 %s = %s %s"
            % (
                utils.irc.bold(coin),
                utils.irc.bold(currency),
                utils.irc.bold(coin),
                utils.irc.bold(price),
                utils.irc.bold(currency),
            )
        )
