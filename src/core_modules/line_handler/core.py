import codecs, re

RE_ISUPPORT_ESCAPE = re.compile(r"\\x(\d\d)", re.I)
RE_MODES = re.compile(r"[-+]\w+")

<<<<<<< HEAD

def ping(event):
    event["server"].send_pong(event["line"].args[0])


=======
def ping(event):
    event["server"].send_pong(event["line"].args[0])

>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
def handle_001(event):
    event["server"].socket.enable_write_throttle()
    event["server"].name = event["line"].source.hostmask
    event["server"].set_own_nickname(event["line"].args[0])
    event["server"].send_whois(event["server"].nickname)
    event["server"].send_mode(event["server"].nickname)
    event["server"].connected = True

<<<<<<< HEAD

=======
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
def handle_005(events, event):
    isupport_list = event["line"].args[1:-1]
    isupport = {}

    for i, item in enumerate(isupport_list):
        key, sep, value = item.partition("=")
        if value:
            for match in RE_ISUPPORT_ESCAPE.finditer(value):
                char = codecs.decode(match.group(1), "hex").decode("ascii")
                value.replace(match.group(0), char)

        if sep:
            isupport[key] = value
        else:
            isupport[key] = None
    event["server"].isupport.update(isupport)

<<<<<<< HEAD
    if "NAMESX" in isupport and not event["server"].has_capability_str("multi-prefix"):
=======
    if "NAMESX" in isupport and not event["server"].has_capability_str(
            "multi-prefix"):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
        event["server"].send_raw("PROTOCTL NAMESX")

    if "PREFIX" in isupport:
        modes, symbols = isupport["PREFIX"][1:].split(")", 1)
        event["server"].prefix_symbols.clear()
        event["server"].prefix_modes.clear()
        for symbol, mode in zip(symbols, modes):
            event["server"].prefix_symbols[symbol] = mode
            event["server"].prefix_modes[mode] = symbol

    if "CHANMODES" in isupport:
        modes = isupport["CHANMODES"].split(",", 3)
        event["server"].channel_list_modes = list(modes[0])
        event["server"].channel_parametered_modes = list(modes[1])
        event["server"].channel_setting_modes = list(modes[2])
        event["server"].channel_modes = list(modes[3])
    if "CHANTYPES" in isupport:
        event["server"].channel_types = list(isupport["CHANTYPES"])
    if "CASEMAPPING" in isupport and isupport["CASEMAPPING"]:
        event["server"].case_mapping = isupport["CASEMAPPING"]
    if "STATUSMSG" in isupport:
        event["server"].statusmsg = list(isupport["STATUSMSG"])
    if "QUIET" in isupport:
        quiet = dict(enumerate(isupport["QUIET"].split(",")))
        prefix = quiet.get(1, "")
<<<<<<< HEAD
        list_numeric = qiuet.get(2, "367")  # RPL_BANLIST
=======
        list_numeric = qiuet.get(2, "367") # RPL_BANLIST
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
        end_numeric = quiet.get(3, "368")  # RPL_ENDOFBANLIST
        event["server"].quiet = [quiet[0], prefix, list_numeric, end_numeric]
    if "TARGMAX" in isupport:
        targmax = {}
        for piece in isupport["TARGMAX"].split(","):
            cmd, _, n = piece.partition(":")
            if n:
                targmax[cmd] = int(n)
        event["server"].targmax = targmax

<<<<<<< HEAD
    events.on("received.005").call(isupport=isupport, server=event["server"])

=======
    events.on("received.005").call(isupport=isupport,
        server=event["server"])
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

def handle_004(event):
    event["server"].version = event["line"].args[2]

<<<<<<< HEAD

def motd_start(event):
    event["server"].motd_lines.clear()


def motd_line(event):
    event["server"].motd_lines.append(event["line"].args[1])


=======
def motd_start(event):
    event["server"].motd_lines.clear()
def motd_line(event):
    event["server"].motd_lines.append(event["line"].args[1])

>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
def _own_modes(server, modes):
    mode_chunks = RE_MODES.findall(modes)
    for chunk in mode_chunks:
        remove = chunk[0] == "-"
        for mode in chunk[1:]:
            server.change_own_mode(remove, mode)

<<<<<<< HEAD

=======
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
def mode(events, event):
    user = event["server"].get_user(event["line"].source.nickname)
    target = event["line"].args[0]
    is_channel = event["server"].is_channel(target)
    if is_channel:
        channel = event["server"].channels.get(target)
        modes = event["line"].args[1]
<<<<<<< HEAD
        args = event["line"].args[2:]
=======
        args  = event["line"].args[2:]
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

        new_modes = channel.parse_modes(modes, args[:])

        events.on("received.mode.channel").call(modes=new_modes,
<<<<<<< HEAD
                                                channel=channel,
                                                server=event["server"],
                                                user=user,
                                                modes_str=modes,
                                                args_str=args)
=======
            channel=channel, server=event["server"], user=user, modes_str=modes,
            args_str=args)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    elif event["server"].is_own_nickname(target):
        modes = event["line"].args[1]
        _own_modes(event["server"], modes)

        events.on("self.mode").call(modes=modes, server=event["server"])
        event["server"].send_who(event["server"].nickname)

<<<<<<< HEAD

def handle_221(event):
    _own_modes(event["server"], event["line"].args[1])


=======
def handle_221(event):
    _own_modes(event["server"], event["line"].args[1])

>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
def invite(events, event):
    target_channel = event["line"].args[1]
    user = event["server"].get_user(event["line"].source.nickname)
    target_user = event["server"].get_user(event["line"].args[0])
<<<<<<< HEAD
    events.on("received.invite").call(user=user,
                                      target_channel=target_channel,
                                      server=event["server"],
                                      target_user=target_user)

=======
    events.on("received.invite").call(user=user, target_channel=target_channel,
        server=event["server"], target_user=target_user)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

def handle_352(events, event):
    nickname = event["line"].args[5]
    username = event["line"].args[2]
    hostname = event["line"].args[3]

    if event["server"].is_own_nickname(nickname):
        event["server"].username = username
        event["server"].hostname = hostname

    target = event["server"].get_user(nickname)
    target.username = username
    target.hostname = hostname
<<<<<<< HEAD
    events.on("received.who").call(server=event["server"], user=target)

=======
    events.on("received.who").call(server=event["server"],
        user=target)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

def handle_354(events, event):
    if event["line"].args[1] == "111":
        nickname = event["line"].args[4]
        username = event["line"].args[2]
        hostname = event["line"].args[3]
        realname = event["line"].args[6]
        account = event["line"].args[5]

        if event["server"].is_own_nickname(nickname):
            event["server"].username = username
            event["server"].hostname = hostname
            event["server"].realname = realname

        target = event["server"].get_user(nickname)
        target.username = username
        target.hostname = hostname
        target.realname = realname
        if not account == "0":
            target.account = account
        else:
            target.account = None
<<<<<<< HEAD
        events.on("received.whox").call(server=event["server"], user=target)

=======
        events.on("received.whox").call(server=event["server"],
            user=target)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

def _nick_in_use(server):
    new_nick = "%s|" % server.connection_params.nickname
    server.send_nick(new_nick)

<<<<<<< HEAD

def handle_433(event):
    _nick_in_use(event["server"])


=======
def handle_433(event):
    _nick_in_use(event["server"])
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
def handle_437(event):
    _nick_in_use(event["server"])
