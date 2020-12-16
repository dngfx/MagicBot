import re

from src import utils


REGEX_307 = re.compile("(plexus-|Unreal3)")


def handle_307(event):
    version = event["server"].version
    if REGEX_307.search(version) is None:
        return

    line = event["line"]

    # ournick = line.args[0]
    nickname = line.args[1]
    idstring = line.args[2]

    if event["server"].is_own_nickname(nickname):
        return

    if idstring.split(" identified for ")[1] == "this nick":
        user = event["server"].get_target(nickname)
        _identified_304(event["server"], user, user.nickname, event)


def _identified_304(server, user, account, event):
    user._id_override = server.get_user_id(account)
    user._account_override = account

    if user.account is None:
        user.account = account


def handle_311(event):
    nickname = event["line"].args[1]
    username = event["line"].args[2]
    hostname = event["line"].args[3]
    realname = event["line"].args[4]

    if event["server"].is_own_nickname(nickname):
        event["server"].username = username
        event["server"].hostname = hostname
        event["server"].realname = realname

    target = event["server"].get_user(nickname)
    target.username = username
    target.hostname = hostname
    target.realname = realname


def quit(events, event):
    nickname = None
    if event["direction"] == utils.Direction.Recv:
        nickname = event["line"].source.nickname
        reason = event["line"].args.get(0)
        if (
            not event["server"].is_own_nickname(nickname)
            and not event["line"].source.hostmask == "*"
        ):
            user = event["server"].get_user(nickname)

            event["server"].quit_user(user)
            events.on("received.quit").call(
                reason=reason, user=user, server=event["server"]
            )

            return True
        else:
            event["server"].disconnect()
            return True
    else:
        return True


def nick(events, event):
    new_nickname = event["line"].args.get(0)
    user = event["server"].get_user(event["line"].source.nickname)
    old_nickname = user.nickname
    user.set_nickname(new_nickname)
    event["server"].change_user_nickname(old_nickname, new_nickname)

    if not event["server"].is_own_nickname(event["line"].source.nickname):
        events.on("received.nick").call(
            new_nickname=new_nickname,
            old_nickname=old_nickname,
            user=user,
            server=event["server"],
        )
    else:
        event["server"].set_own_nickname(new_nickname)
        events.on("self.nick").call(
            server=event["server"], new_nickname=new_nickname, old_nickname=old_nickname
        )


def away(events, event):
    user = event["server"].get_user(event["line"].source.nickname)
    message = event["line"].args.get(0)
    if message:
        user.away = True
        user.away_message = message
        events.on("received.away.on").call(
            user=user, server=event["server"], message=message
        )
    else:
        user.away = False
        user.away_message = None
        events.on("received.away.off").call(user=user, server=event["server"])


def chghost(events, event):
    nickname = event["line"].source.nickname
    username = event["line"].args[0]
    hostname = event["line"].args[1]

    if event["server"].is_own_nickname(nickname):
        event["server"].username = username
        event["server"].hostname = hostname

    target = event["server"].get_user(nickname)

    old_username = target.username
    old_hostname = target.hostname
    target.username = username
    target.hostname = hostname

    events.on("received.chghost").call(
        user=target,
        server=event["server"],
        old_username=old_username,
        old_hostname=old_hostname,
    )


def setname(event):
    nickname = event["line"].source.nickname
    realname = event["line"].args[0]

    user = event["server"].get_user(nickname)
    user.realname = realname

    if event["server"].is_own_nickname(nickname):
        event["server"].realname = realname


def account(events, event):
    user = event["server"].get_user(event["line"].source.nickname)

    if not event["line"].args[0] == "*":
        user.account = event["line"].args[0]
        events.on("received.account.login").call(
            user=user, server=event["server"], account=event["line"].args[0]
        )
    else:
        account = user.account
        user.account = None
        events.on("received.account.logout").call(
            user=user, server=event["server"], account=account
        )
