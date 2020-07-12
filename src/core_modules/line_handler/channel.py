from src import IRCLine, utils

<<<<<<< HEAD

=======
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
def handle_332(events, event):
    channel = event["server"].channels.get(event["line"].args[1])
    topic = event["line"].args.get(2)
    channel.set_topic(topic)
<<<<<<< HEAD
    events.on("received.332").call(channel=channel, server=event["server"], topic=topic)

=======
    events.on("received.332").call(channel=channel, server=event["server"],
        topic=topic)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

def topic(events, event):
    user = event["server"].get_user(event["line"].source.nickname)
    channel = event["server"].channels.get(event["line"].args[0])
    topic = event["line"].args.get(1)
    channel.set_topic(topic)
<<<<<<< HEAD
    events.on("received.topic").call(channel=channel, server=event["server"], topic=topic, user=user)

=======
    events.on("received.topic").call(channel=channel, server=event["server"],
        topic=topic, user=user)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

def handle_333(events, event):
    channel = event["server"].channels.get(event["line"].args[1])

    topic_setter = IRCLine.parse_hostmask(event["line"].args[2])
    topic_time = int(event["line"].args[3])

    channel.set_topic_setter(topic_setter)
    channel.set_topic_time(topic_time)
<<<<<<< HEAD
    events.on("received.333").call(channel=channel, setter=topic_setter, set_at=topic_time, server=event["server"])

=======
    events.on("received.333").call(channel=channel,
        setter=topic_setter, set_at=topic_time, server=event["server"])
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

def handle_353(event):
    channel = event["server"].channels.get(event["line"].args[2])
    nicknames = event["line"].args.get(3).split(" ")

    # there can sometimes be a dangling space at the end of a 353
    if nicknames and not nicknames[-1]:
        nicknames.pop(-1)

    for nickname in nicknames:
        modes = set([])

        while nickname[0] in event["server"].prefix_symbols:
            modes.add(event["server"].prefix_symbols[nickname[0]])
            nickname = nickname[1:]

        if event["server"].has_capability_str("userhost-in-names"):
            hostmask = IRCLine.parse_hostmask(nickname)
            nickname = hostmask.nickname
<<<<<<< HEAD
            user = event["server"].get_user(hostmask.nickname, username=hostmask.username, hostname=hostmask.hostname)
=======
            user = event["server"].get_user(hostmask.nickname,
                username=hostmask.username, hostname=hostmask.hostname)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
        else:
            user = event["server"].get_user(nickname)
        user.join_channel(channel)
        channel.add_user(user)

        for mode in modes:
            channel.add_mode(mode, nickname)

<<<<<<< HEAD

def handle_366(event):
    event["server"].send_whox(event["line"].args[1], "n", "ahnrtu", "111")


=======
def handle_366(event):
    event["server"].send_whox(event["line"].args[1], "n", "ahnrtu", "111")

>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
def join(events, event):
    account = None
    realname = None
    channel_name = event["line"].args[0]

    if len(event["line"].args) == 3:
        if not event["line"].args[1] == "*":
            account = event["line"].args[1]
        realname = event["line"].args[2]

    user = event["server"].get_user(event["line"].source.nickname,
<<<<<<< HEAD
                                    username=event["line"].source.username,
                                    hostname=event["line"].source.hostname)
=======
        username=event["line"].source.username,
        hostname=event["line"].source.hostname)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

    if account:
        user.account = account
    if realname:
        user.realname = realname

    is_self = event["server"].is_own_nickname(event["line"].source.nickname)
    if is_self:
        channel = event["server"].channels.add(channel_name)
    else:
        channel = event["server"].channels.get(channel_name)

<<<<<<< HEAD
=======

>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    channel.add_user(user)
    user.join_channel(channel)

    if is_self:
        channel.send_mode()
<<<<<<< HEAD
        events.on("self.join").call(channel=channel, server=event["server"], account=account, realname=realname)
    else:
        events.on("received.join").call(channel=channel,
                                        user=user,
                                        server=event["server"],
                                        account=account,
                                        realname=realname)

=======
        events.on("self.join").call(channel=channel, server=event["server"],
            account=account, realname=realname)
    else:
        events.on("received.join").call(channel=channel, user=user,
            server=event["server"], account=account, realname=realname)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

def part(events, event):
    channel = event["server"].channels.get(event["line"].args[0])
    user = event["server"].get_user(event["line"].source.nickname)
    reason = event["line"].args.get(1)

    event["server"].part_user(channel, user)

    if not event["server"].is_own_nickname(event["line"].source.nickname):
<<<<<<< HEAD
        events.on("received.part").call(channel=channel, reason=reason, user=user, server=event["server"])
=======
        events.on("received.part").call(channel=channel, reason=reason,
            user=user, server=event["server"])
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
    else:
        event["server"].channels.remove(channel)
        for user in channel.users.copy():
            event["server"].part_user(channel, user)

<<<<<<< HEAD
        events.on("self.part").call(channel=channel, reason=reason, server=event["server"])

=======
        events.on("self.part").call(channel=channel, reason=reason,
            server=event["server"])
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

def handle_324(events, event):
    if event["line"].args[1] in event["server"].channels:
        channel = event["server"].channels.get(event["line"].args[1])
        channel.seen_modes = True
        modes = event["line"].args[2]
        args = event["line"].args[3:]
        new_modes = channel.parse_modes(modes, args[:])
        events.on("received.324").call(modes=new_modes,
<<<<<<< HEAD
                                       channel=channel,
                                       server=event["server"],
                                       mode_str=modes,
                                       args_str=args)

=======
            channel=channel, server=event["server"], mode_str=modes,
            args_str=args)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

def handle_329(event):
    if event["line"].args[1] in event["server"].channels:
        channel = event["server"].channels.get(event["line"].args[1])
        channel.creation_timestamp = int(event["line"].args[2])

<<<<<<< HEAD

def handle_477(timers, event):
    pass


=======
def handle_477(timers, event):
    pass

>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
def kick(events, event):
    user = event["server"].get_user(event["line"].source.nickname)
    target = event["line"].args[1]
    channel = event["server"].channels.get(event["line"].args[0])
    reason = event["line"].args.get(2)
    target_user = event["server"].get_user(target)

    if not event["server"].is_own_nickname(target):
<<<<<<< HEAD
        events.on("received.kick").call(channel=channel,
                                        reason=reason,
                                        target_user=target_user,
                                        user=user,
                                        server=event["server"])
    else:
        event["server"].channels.remove(channel)
        events.on("self.kick").call(channel=channel, reason=reason, user=user, server=event["server"])
=======
        events.on("received.kick").call(channel=channel, reason=reason,
            target_user=target_user, user=user, server=event["server"])
    else:
        event["server"].channels.remove(channel)
        events.on("self.kick").call(channel=channel, reason=reason, user=user,
            server=event["server"])
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

    channel.remove_user(target_user)
    target_user.part_channel(channel)

<<<<<<< HEAD

=======
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
def rename(events, event):
    old_name = event["line"].args[0]
    new_name = event["line"].args[1]
    channel = event["server"].channels.get(old_name)

    event["server"].channels.rename(old_name, new_name)
<<<<<<< HEAD
    events.on("received.rename").call(channel=channel,
                                      old_name=old_name,
                                      new_name=new_name,
                                      reason=event["line"].args.get(2),
                                      server=event["server"])
=======
    events.on("received.rename").call(channel=channel, old_name=old_name,
        new_name=new_name, reason=event["line"].args.get(2),
        server=event["server"])
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
