#--depends-on commands
#--depends-on config
#--require-config avwx-api-key

#https://avwx.rest/api/metar/location?options=&airport=true&reporting=true&format=json&onfail=cache

METAR_URL = "https://avwx.rest/api/metar/%s"

from src import ModuleManager, utils


class Module(ModuleManager.BaseModule):
    _name = "METAR"

    @utils.hook("received.command.metar")
    @utils.kwarg("help", "Get a METAR report")
    @utils.spec("!<icao>lstring")
    def get_metar_report(self, event, title=None):
        location = event["spec"][0]
        print(location)

        page = utils.http.request(METAR_URL % location,
                                  get_params={
                                      "options": "info",
                                      "format": "json",
                                      "token": self.bot.config["avwx-api-key"]
                                  }).json()

        if "error" in page:
            event["stderr"].write(page["error"])
            return

        info = page["info"]
        units = page["units"]
        name = utils.irc.bold(info["name"])
        temp_num = page["temperature"]["value"]
        temp_unit = units["temperature"]
        wind_num = page["wind_speed"]["value"]
        wind_unit = units["wind_speed"]
        vis_num = page["visibility"]["value"]
        vis_unit = units["visibility"]
        alt_num = page["altimeter"]["value"]
        alt_unit = units["altimeter"]
        dew = page["dewpoint"]["value"]

        visibility = "%s: %s%s" % (utils.irc.bold("Visibility"), vis_num, vis_unit)
        temperature = "%s: %s%s" % (utils.irc.bold("Temperature"), temp_num, temp_unit)
        windspeed = "%s: %s %s" % (utils.irc.bold("Windspeed"), wind_num, wind_unit)
        altimiter = "%s: %s %s" % (utils.irc.bold("Altimeter"), alt_num, alt_unit)
        readout = "%s: %s" % (utils.irc.bold("Readout"), page["sanitized"])
        dewpoint = "%s: %s%s" % (utils.irc.bold("Dew Point"), dew, temp_unit)

        event["stdout"].write("Information for %s: %s — %s — %s — %s — %s — %s" % (name,
                                                                                   visibility,
                                                                                   temperature,
                                                                                   windspeed,
                                                                                   altimiter,
                                                                                   dewpoint,
                                                                                   readout))
