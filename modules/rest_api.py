#--depends-on commands
#--depends-on config
#--depends-on permissions

import binascii
import http.server
import json
import os
import socket
import threading
import urllib.parse

from src import ModuleManager, utils
from src.Logging import Logger as log


DEFAULT_PORT = 5001
DEFAULT_PUBLIC_PORT = 5000


class Response(object):

    def __init__(self, compact=False):
        self._compact = compact
        self._headers = {}
        self._data = b""
        self.code = 200
        self.content_type = "text/plain"

    def write(self, data):
        self._data += data

    def write_text(self, data):
        self._data += data.encode("utf8")

    def write_json(self, obj):
        if self._compact:
            data = json.dumps(obj, separators=(",", ":"))
        else:
            data = json.dumps(obj, sort_keys=True, indent=4)
        self._data += data.encode("utf8")

    def set_header(self, key: str, value: str):
        self._headers[key] = value

    def get_headers(self):
        headers = {}
        has_content_type = False
        for key, value in self._headers.items():
            if key.lower() == "content-type":
                has_content_type = True
            headers[key] = value
        if not has_content_type:
            headers["Content-Type"] = self.content_type
        headers["Content-Length"] = len(self._data)
        return headers

    def get_data(self):
        return self._data


_module = None
_bot = None
_events = None
_log = None


class Handler(http.server.BaseHTTPRequestHandler):
    timeout = 10

    def _path_data(self):
        path = urllib.parse.urlparse(self.path).path
        _, _, endpoint = path[1:].partition("/")
        endpoint, _, args = endpoint.partition("/")
        args = list(filter(None, args.split("/")))
        return path, endpoint, args

    def _url_params(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        return dict([(k, v[0]) for k, v in query.items()])

    def _body(self):
        content_length = int(self.headers.get("content-length", 0))
        return self.rfile.read(content_length)

    def _respond(self, response):
        self.send_response(response.code)
        for key, value in response.get_headers().items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(response.get_data())

    def _key_settings(self, key):
        return _bot.get_setting("api-key-%s" % key,
                                {})

    def _minify_setting(self):
        return _bot.get_setting("rest-api-minify", False)

    def _url_for(self, headers):
        return (
            lambda route,
            endpoint,
            args=[],
            get_params={}: _module._url_for(route,
                                            endpoint,
                                            args,
                                            get_params,
                                            headers.get("Host",
                                                        None))
        )

    def _handle(self, method, path, endpoint, args):
        headers = utils.CaseInsensitiveDict(dict(self.headers.items()))
        params = self._url_params()
        data = self._body()

        response = Response(compact=self._minify_setting())
        response.code = 404

        hooks = _events.on("api").on(method).on(endpoint).get_hooks()
        if hooks:
            response.code = 200
            hook = hooks[0]
            authenticated = hook.get_kwarg("authenticated", True)
            key = params.get("key", None)
            key_setting = self._key_settings(key)
            permissions = key_setting.get("permissions", [])

            if key_setting:
                log.debug(log, "[HTTP] %s to %s with API key %s (%s)" % (method, path, key, key_setting["comment"]))

            if authenticated or path in permissions or "*" in permissions:
                event_response = None
                event_response = _events.on("api").on(method).on(endpoint).call_for_result_unsafe(
                    params=params,
                    args=args,
                    data=data,
                    headers=headers,
                    response=response,
                    url_for=self._url_for(headers)
                )
                """except Exception as e:
                    log.error(log, "failed to call API endpoint \"%s\"" % (path))
                    response.code = 500"""

            if event_response != None:
                response.write_json(event_response)
                response.content_type = "application/json"
            else:
                response.code = 401
        return response

    def _handle_wrap(self, method):
        path, endpoint, args = self._path_data()
        log.debug(
            log,
            "[HTTP] starting _handle for %s from %s:%d: %s" %
            (method,
             self.client_address[0],
             self.client_address[1],
             path)
        )

        response = _bot.trigger(lambda: self._handle(method, path, endpoint, args))
        self._respond(response)

        log.debug(
            log,
            "[HTTP] finishing _handle for %s from %s:%d (%d)" %
            (method,
             self.client_address[0],
             self.client_address[1],
             response.code)
        )

    def do_GET(self):
        self._handle_wrap("GET")

    def do_POST(self):
        self._handle_wrap("POST")

    def log_message(self, format, *args):
        return


class BitBotIPv6HTTPd(http.server.HTTPServer):
    address_family = socket.AF_INET6


@utils.export("botset", utils.BoolSetting("rest-api", "Enable/disable REST API"))
@utils.export("botset", utils.BoolSetting("rest-api-minify", "Enable/disable REST API minifying"))
@utils.export("botset", utils.Setting("rest-api-host", "Public hostname:port for the REST API"))
class Module(ModuleManager.BaseModule):
    _name = "REST"

    def on_load(self):
        global _module
        _module = self

        global _bot
        _bot = self.bot

        global _events
        _events = self.events

        self.httpd = None
        if self.bot.get_setting("rest-api", False):
            self._start_httpd()

    def _start_httpd(self):
        port = int(self.bot.config.get("api-port", str(DEFAULT_PORT)))
        self.httpd = BitBotIPv6HTTPd(("::1", port), Handler)

        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    def _stop_httpd(self):
        if self.httpd:
            self.httpd.shutdown()

    def on_resume(self):
        self._start_httpd()

    def unload(self):
        self._stop_httpd()

    def on_pause(self):
        self._stop_httpd()

    @utils.hook("received.command.apikey")
    @utils.kwarg("private_only", True)
    @utils.spec("!'list ?<alias>wordlower")
    @utils.spec("!'add !<alias>wordlower ?<endpoints>words")
    @utils.spec("!'remove !<alias>wordlower")
    @utils.kwarg("permission", "apikey")
    def apikey(self, event):
        subcommand = event["spec"][0]
        alias = event["spec"][1]
        found = None

        api_keys = {}
        for key, value in self.bot.find_settings(prefix="api-key-"):
            api_keys[key] = value
            if alias and value["comment"].lower() == alias:
                found = key

        if subcommand == "list":
            aliases = {v["comment"]: v
                       for v in api_keys.values()}
            if alias:
                if not alias in aliases:
                    event["stderr"].write("API key '%s' not found" % alias)
                event["stdout"].write(
                    "API key %s ('%s') can access: %s" % (key,
                                                          alias,
                                                          " ".join(aliases[alias]["permissions"]))
                )
            else:
                event["stdout"].write("API keys: %s" % ", ".join(sorted(aliases.keys())))
        elif subcommand == "add":
            if found == None:
                new_key = binascii.hexlify(os.urandom(16)).decode("ascii")
                self.bot.set_setting("api-key-%s" % new_key,
                                     {
                                         "comment": alias,
                                         "permissions": event["spec"][2] or []
                                     })
                event["stdout"].write("New API key '%s': %s" % (alias, new_key))
            else:
                event["stderr"].write("API key alias '%s' already exists" % alias)
        elif subcommand == "remove":
            if not len(event["args_split"]) > 1:
                raise utils.EventError("Please provide a key alias to remove")

            if not found == None:
                self.bot.del_setting(found)
                key = found.replace("api-key-", "", 1)
                event["stdout"].write("Deleted API key %s ('%s')" % (key, alias))
            else:
                event["stderr"].write("Count not find API key '%s'" % alias)

    @utils.export("url-for")
    def _url_for(self,
                 route,
                 endpoint,
                 args=[],
                 get_params={},
                 host_override=None):
        host = host_override or self.bot.get_setting("rest-api-host", None)

        host, _, port = host.partition(":")
        if not port:
            port = str(_bot.config.get("api-port", DEFAULT_PUBLIC_PORT))
        host = "%s:%s" % (host, port)

        if host:
            args_str = ""
            if args:
                args_str = "/%s" % "/".join(args)
            get_params_str = ""
            if get_params:
                get_params_str = "?%s" % urllib.parse.urlencode(get_params)
            return "%s/%s/%s%s%s" % (host, route, endpoint, args_str, get_params_str)
        else:
            return None
