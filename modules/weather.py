# --depends-on commands
# --depends-on location
# --require-config openweathermap-api-key

from src import ModuleManager, utils
import datetime, time

URL_WEATHER = "http://api.openweathermap.org/data/2.5/weather"
URL_FORECAST = "http://api.openweathermap.org/data/2.5/forecast"


class Module(ModuleManager.BaseModule):
    def _user_location(self, user):
        user_location = user.get_setting("location", None)
        if user_location is not None:
            name = user_location.get("name", None)
            return [user_location["lat"], user_location["lon"], name]

    def _weather_colour(self, cel, temp, unit):
        color = temp
        temp = "%s%s" % (temp, unit)
        if cel <= 0:
            color = utils.irc.color(temp, utils.consts.BLUE)
        if 0 < cel <= 10:
            color = utils.irc.color(temp, utils.consts.LIGHTGREEN)
        if cel > 10 and cel <= 20:
            color = utils.irc.color(temp, utils.consts.GREEN)
        if cel > 20 and cel <= 25:
            color = utils.irc.color(temp, utils.consts.YELLOW)
        if cel > 25 and cel <= 30:
            color = utils.irc.color(temp, utils.consts.ORANGE)
        if cel > 30:
            color = utils.irc.color(temp, utils.consts.RED)
        return color

    @utils.hook("received.command.w", alias_of="weather")
    @utils.hook("received.command.weather")
    def weather(self, event):
        api_key = self.bot.config["openweathermap-api-key"]

        location = None
        query = None
        nickname = None
        if event["args"]:
            query = event["args"]
            if len(event["args_split"]) == 1 and event["server"].has_user_id(
                event["args_split"][0]
            ):
                target_user = event["server"].get_user(event["args_split"][0])
                location = self._user_location(target_user)
                if location is not None:
                    nickname = target_user.nickname
            else:
                location = event["args_split"][0]
        else:
            location = self._user_location(event["user"])
            nickname = event["user"].nickname
            if location is None:
                raise utils.EventError("You don't have a location set")

        args = {"units": "metric", "APPID": api_key}

        if location is not None and query:
            location_info = self.exports.get_one("get-location")(query)
            if location_info is not None:
                location = [
                    location_info["lat"],
                    location_info["lon"],
                    location_info.get("name", None),
                ]
        if location is None:
            raise utils.EventError("Unknown location")

        lat, lon, location_name = location
        args["lat"] = lat
        args["lon"] = lon

        page = utils.http.request(URL_WEATHER, get_params=args).json()
        if page:
            if "weather" in page:
                if location_name:
                    location_str = location_name

                    place_name = (
                        page["sys"]["name"] if "name" in page["sys"] else page["name"]
                    )

                    if place_name != location_str.split(",")[0]:
                        location_str = "%s, %s" % (place_name, location_name)
                else:
                    location_parts = [page["name"]]
                    if "country" in page["sys"]:
                        location_parts.append(page["sys"]["country"])
                    location_str = ", ".join(location_parts)

                celsius_color = page["main"]["temp"]
                celsius = self._weather_colour(celsius_color, page["main"]["temp"], "C")
                fahrenheit = self._weather_colour(
                    celsius_color, round(page["main"]["temp"] * (9 / 5)) + 32, "F"
                )
                description = page["weather"][0]["description"].title()
                humidity = "%s%%" % page["main"]["humidity"]

                # wind speed is in metres per second - 3.6* for KMh
                wind_speed = 3.6 * page["wind"]["speed"]
                wind_speed_k = "%sKMh" % round(wind_speed, 1)
                wind_speed_m = "%sMPh" % round(0.6214 * wind_speed, 1)

                if nickname is not None:
                    location_str = "(%s) %s" % (nickname, location_str)

                event["stdout"].write(
                    "%s | %s/%s | %s | Humidity: %s | Wind: %s/%s"
                    % (
                        location_str,
                        celsius,
                        fahrenheit,
                        description,
                        humidity,
                        wind_speed_k,
                        wind_speed_m,
                    )
                )
            else:
                event["stderr"].write("No weather information for this location")
        else:
            raise utils.EventResultsError()

    @utils.hook("received.command.f", alias_of="forecast")
    @utils.hook("received.command.forecast")
    def forecast(self, event):
        """
        :help: Get current weather for you or someone else
        :usage: [nickname]
        :require_setting: location
        :require_setting_unless: 1
        """
        api_key = self.bot.config["openweathermap-api-key"]

        location = None
        query = None
        nickname = None
        if event["args"]:
            query = event["args"]
            if len(event["args_split"]) == 1 and event["server"].has_user_id(
                event["args_split"][0]
            ):
                target_user = event["server"].get_user(event["args_split"][0])
                location = self._user_location(target_user)
                if location is not None:
                    nickname = target_user.nickname
            else:
                location = event["args_split"][0]
        else:
            location = self._user_location(event["user"])
            nickname = event["user"].nickname
            if location is None:
                raise utils.EventError("You don't have a location set")

        args = {"units": "metric", "APPID": api_key}

        if location is not None and query:
            location_info = self.exports.get_one("get-location")(query)
            if location_info is not None:
                location = [
                    location_info["lat"],
                    location_info["lon"],
                    location_info.get("name", None),
                ]
        if location is None:
            raise utils.EventError("Unknown location")

        lat, lon, location_name = location
        args["lat"] = lat
        args["lon"] = lon
        location_str = location_name

        page = utils.http.request(URL_FORECAST, get_params=args).json()

        if "list" not in page:
            event["stderr"].write("No weather information for this location")
            return

        forecast = []
        forecast_str = []
        day_last = ""
        dt = datetime.datetime.fromtimestamp(int(time.time()))
        today = datetime.datetime.strftime(dt, "%a")

        forecast_list = page["list"]
        for page in forecast_list:

            dt = datetime.datetime.fromtimestamp(page["dt"])
            day = datetime.datetime.strftime(dt, "%a")

            if day_last == day or day == today:
                continue
            else:
                day_last = day

            celsius_color = page["main"]["temp"]
            celsius = self._weather_colour(celsius_color, page["main"]["temp"], "C")
            fahrenheit = self._weather_colour(
                celsius_color, round(page["main"]["temp"] * (9 / 5)) + 32, "F"
            )
            # fahrenheit = "%dF" % ((page["main"]["temp"] * (9 / 5)) + 32)
            description = page["weather"][0]["description"].title()

            # wind speed is in metres per second - 3.6* for KMh
            wind_speed = 3.6 * page["wind"]["speed"]
            wind_speed_k = "%sKMh" % round(wind_speed, 1)
            wind_speed_m = "%sMPh" % round(0.6214 * wind_speed, 1)

            forecast_day_str = "%s: %s/%s | %s | Wind: %s/%s" % (
                utils.irc.bold(day),
                celsius,
                fahrenheit,
                description,
                wind_speed_k,
                wind_speed_m,
            )

            forecast_str.append(forecast_day_str)

        forecast_final = " —— ".join(forecast_str)
        event["stdout"].write("Forecast for %s: %s" % (location_str, forecast_final))
