# --depends-on commands

from src import EventManager, ModuleManager, utils
import time
import pprint


HOSTMASKS_SETTING = "hostmask-account"
NO_PERMISSION = "You do not have permission to do that"
ACCOUNT_TAG = utils.irc.MessageTag("account")


class Module(ModuleManager.BaseModule):
    whois_nicks = []
    init_nicks = []

    @utils.hook("new.server")
    def new_server(self, event):
        event["server"]._hostmasks = {}

        for account, user_hostmasks in event["server"].get_all_user_settings(
            HOSTMASKS_SETTING
        ):
            for hostmask in user_hostmasks:
                self._add_hostmask(
                    event["server"], utils.irc.hostmask_parse(
                        hostmask), account
                )

    def _add_hostmask(self, server, hostmask, account):
        server._hostmasks[hostmask.original] = (hostmask, account)

    def _remove_hostmask(self, server, hostmask):
        if hostmask in server._hostmasks:
            del server._hostmasks[hostmask]

    def _make_hash(self, password, salt=None):
        salt = salt or utils.security.salt()
        hash = utils.security.hash(salt, password)
        return hash, salt

    def _get_hash(self, server, account):
        hash, salt = server.get_user(account).get_setting(
            "authentication", (None, None)
        )
        return hash, salt

    def _master_password(self):
        master_password = utils.security.password()
        hash, salt = self._make_hash(master_password)
        self.bot.set_setting("master-password", [hash, salt])
        return master_password

    @utils.hook("control.master-password")
    def command_line(self, event):
        master_password = self._master_password()
        return "One-time master password: %s" % master_password

    def _has_identified(self, server, user, account):
        user._id_override = server.get_user_id(account)
        self.events.on("internal.identified").call(
            server=server, user=user, account=account
        )

    @utils.export("is-identified")
    def _is_identified(self, server, user):
        has_override = user._account_override is None and user.account is None
        if not has_override:
            return True
        else:
            return False

    def _signout(self, user):
        user._id_override = None

    def _find_hostmask(self, server, user):
        user_hostmask = user.hostmask()
        for hostmask, (hostmask_pattern, account) in server._hostmasks.items():
            if utils.irc.hostmask_match(user_hostmask, hostmask_pattern):
                return (hostmask, account)

    def _specific_hostmask(self, server, hostmask, account):
        for user in server.users.values():
            if utils.irc.hostmask_match(user.hostmask(), hostmask):
                if account == None:
                    user._hostmask_account = None
                    self._signout(user)
                else:
                    user._hostmask_account = (hostmask, account)
                    self._has_identified(server, user, account)

    @utils.export("account-name")
    def _account_name(self, user):
        if not user.account == None:
            return user.account
        elif not user._account_override == None:
            return user._account_override
        elif not user._hostmask_account == None:
            return user._hostmask_account[1]

    @utils.hook("new.user")
    def new_user(self, event):
        nick = event["user"].nickname_lower
        if event["server"].is_own_nickname(nick) or nick == "py-ctcp":
            return

        """user = event["server"].fetch_user(event["user"].nickname_lower)

        user._hostmask_account = None
        user._account_override = None
        user._master_admin = False
        user._sent_who = time.time()

        if nick not in self.init_nicks:
            self.init_nicks.append(nick)
            self._is_identified(event["server"], event["user"])"""

    def _set_hostmask(self, server, user):
        account = self._find_hostmask(server, user)
        if not account == None:
            hostmask, account = account
            user._hostmask_account = (hostmask, account)
            self._has_identified(server, user, account)

    @utils.hook("received.message.private")
    @utils.hook("received.message.channel")
    def _priv_msg(self, event):
        if event["user"].nickname_lower not in self.init_nicks:
            self.new_user(event)
            event["server"].send_who(event["user"].nickname_lower)
            self._is_identified(event["server"], event["user"])

    @utils.hook("received.chghost")
    @utils.hook("received.nick")
    @utils.hook("received.who")
    @utils.hook("received.whox")
    def chghost(self, event):
        if not self._is_identified(event["server"], event["user"]):
            self._set_hostmask(event["server"], event["user"])

            if event["user"].is_identified is True:
                event["user"].account = event["user"].nickname_lower
                print(event["user"])

    @utils.hook("received.whox")
    @utils.hook("received.account")
    @utils.hook("received.account.login")
    @utils.hook("received.account.logout")
    @utils.hook("received.join")
    def check_account(self, event):
        if not self._is_identified(event["server"], event["user"]):
            if event["user"].account:
                self._has_identified(
                    event["server"], event["user"], event["user"].account
                )
            else:
                self._set_hostmask(event["server"], event["user"])

    @utils.hook("received.message.private")
    @utils.hook("received.message.channel")
    @utils.kwarg("priority", EventManager.PRIORITY_HIGH)
    def account_tag(self, event):
        account = ACCOUNT_TAG.get_value(event["line"].tags)
        if not self._is_identified(event["server"], event["user"]):
            if not account == None:
                self._has_identified(event["server"], event["user"], account)

    def _get_permissions(self, server, user):
        if self._is_identified(server, user):
            return user.get_setting("permissions", [])
        return []

    def _has_permission(self, server, user, permission):
        if user._master_admin:
            return True

        permissions = self._get_permissions(server, user)
        if "*" in permissions:
            return True

        if permission in permissions:
            return True
        else:
            permission_parts = permission.split(".")
            for user_permission in permissions:
                user_permission_parts = user_permission.split(".")
                for i, part in enumerate(permission_parts):
                    last = i == (len(permission_parts) - 1)
                    user_last = i == (len(user_permission_parts) - 1)
                    if not permission_parts[i] == user_permission_parts[i]:
                        if user_permission_parts[i] == "*" and user_last:
                            return True
                        else:
                            break
                    else:
                        if last and user_last:
                            return True
        return False

    @utils.hook("received.command.masterlogin")
    @utils.kwarg("min_args", 1)
    @utils.kwarg("private_only", True)
    def master_login(self, event):
        saved_hash, saved_salt = self.bot.get_setting(
            "master-password", (None, None))
        if saved_hash and saved_salt:
            if utils.security.hash_verify(saved_salt, event["args"], saved_hash):
                self.bot.del_setting("master-password")
                event["user"]._master_admin = True
                event["stdout"].write("Master login successful")
                return
        event["stderr"].write("Master login failed")

    @utils.hook("received.command.mypermissions")
    @utils.kwarg("authenticated", True)
    def my_permissions(self, event):
        """
        :help: Show your permissions
        """
        permissions = event["user"].get_setting("permissions", [])
        event["stdout"].write("Your permissions: %s" % ", ".join(permissions))

    @utils.hook("received.command.register")
    @utils.kwarg("help", "Register your nickname")
    @utils.spec("!-privateonly !<password>string")
    def register(self, event):
        hash, salt = self._get_hash(event["server"], event["user"].nickname)
        if not hash and not salt:
            password = event["args"]
            hash, salt = self._make_hash(password)
            event["user"].set_setting("authentication", [hash, salt])

            event["user"]._account_override = event["user"].nickname
            self._has_identified(
                event["server"], event["user"], event["user"].nickname)

            event["stdout"].write("Nickname registered successfully")
        else:
            event["stderr"].write("This nickname is already registered")

    @utils.hook("received.command.identify")
    @utils.kwarg("help", "Identify for your current nickname")
    @utils.spec("!-privateonly ?<account>aword !<password>string")
    def identify(self, event):
        if not event["user"].channels:
            raise utils.EventError(
                "You must share at least one channel " "with me before you can identify"
            )

        if not self._is_identified(event["user"]):
            account = event["spec"][0] or event["user"].nickname
            password = event["spec"][1]

            hash, salt = self._get_hash(event["server"], account)
            if hash and salt:
                if utils.security.hash_verify(salt, password, hash):
                    event["user"]._account_override = account
                    self._has_identified(
                        event["server"], event["user"], account)

                    event["stdout"].write(
                        "Correct password, you have " "been identified as %s." % account
                    )
                else:
                    event["stderr"].write(
                        "Incorrect password for '%s'" % account)
            else:
                event["stderr"].write(
                    "Account '%s' is not registered" % account)
        else:
            event["stderr"].write(
                "You are already identified as %s" % self._account_name(
                    event["user"])
            )

    @utils.hook("received.command.permission")
    @utils.spec("!'list,clear !<nickname>ouser")
    @utils.spec("!'add,remove !<nickname>ouser !<permission>tstring")
    @utils.kwarg("permission", "permissions.change")
    def permission(self, event):
        subcommand = event["spec"][0].lower()
        target_user = event["spec"][1]

        if subcommand == "list":
            event["stdout"].write(
                "Permissions for %s: %s"
                % (
                    target_user.nickname,
                    ", ".join(self._get_permissions(
                        event["server"], target_user)),
                )
            )
        elif subcommand == "clear":
            if not self._get_permissions(event["server"], target_user):
                raise utils.EventError(
                    "%s has no permissions" % target_user.nickname)
            target_user.del_setting("permissions")
            event["stdout"].write(
                "Cleared permissions for %s" % target_user.nickname)
        else:
            permissions = event["spec"][2].split()
            user_permissions = self._get_permissions(
                event["server"], target_user)

            if subcommand == "add":
                new = list(set(permissions) - set(user_permissions))
                if not new:
                    raise utils.EventError("No new permissions to give")
                target_user.set_setting("permissions", user_permissions + new)
                event["stdout"].write(
                    "Gave %s new permissions: %s"
                    % (target_user.nickname, ", ".join(new))
                )
            elif subcommand == "remove":
                permissions_set = set(permissions)
                user_permissions_set = set(user_permissions)
                removed = list(user_permissions_set & permissions_set)
                if not (user_permissions_set & permissions_set):
                    raise utils.EventError("New permissions to remove")
                change = list(user_permissions_set - permissions_set)

                if not change:
                    target_user.del_setting("permissions")
                else:
                    target_user.set_setting("permissions", change)
                event["stdout"].write(
                    "Removed permissions from %s: %s"
                    % (target_user.nickname, ", ".join(change))
                )
            else:
                raise utils.EventError("Unknown subcommand %s" % subcommand)

    @utils.hook("received.command.hostmask")
    @utils.kwarg("authenticated", True)
    @utils.spec("!'list")
    @utils.spec("!'add,remove ?<hostmask>word")
    def hostmask(self, event):
        subcommand = event["spec"][0]
        hostmasks = event["user"].get_setting(HOSTMASKS_SETTING, [])

        if subcommand == "list":
            event["stdout"].write("Your hostmasks: %s" % ", ".join(hostmasks))
        else:
            hostmask = event["spec"][1]
            account = self._account_name(event["user"])

            if subcommand == "add":
                if hostmask in hostmasks:
                    raise utils.EventError(
                        "Hostmask %s is already on your account" % hostmask
                    )
                hostmasks.append(hostmask)
                event["user"].set_setting(HOSTMASKS_SETTING, hostmasks)

                hostmask_obj = utils.irc.hostmask_parse(hostmask)
                self._specific_hostmask(event["server"], hostmask_obj, account)
                self._add_hostmask(event["server"], hostmask_obj, account)

                event["stdout"].write("Added %s to your hostmasks" % hostmask)
            elif subcommand == "remove":
                if not hostmask in hostmasks:
                    raise utils.EventError(
                        "Hostmask %s is not on your account" % hostmask
                    )
                while hostmask in hostmasks:
                    hostmasks.remove(hostmask)
                event["user"].set_setting(HOSTMASKS_SETTING, hostmasks)

                self._specific_hostmask(event["server"], hostmask, None)
                self._remove_hostmask(event["server"], hostmask)

                event["stdout"].write(
                    "Removed %s from your hostmasks" % hostmask)
            else:
                raise utils.EventError("Unknown subcommand %s" % subcommand)

    def _assert(self, allowed):
        if allowed:
            return utils.consts.PERMISSION_FORCE_SUCCESS, None
        else:
            return utils.consts.PERMISSION_ERROR, NO_PERMISSION

    @utils.hook("preprocess.command")
    def preprocess_command(self, event):
        allowed = None
        permission = event["hook"].get_kwarg("permission", None)
        authenticated = event["hook"].get_kwarg("authenticated", False)
        if not permission == None:
            allowed = self._has_permission(
                event["server"], event["user"], permission)
        elif authenticated:
            allowed = self._is_identified(event["server"], event["user"])
        else:
            return

        return self._assert(allowed)

    @utils.hook("check.command.permission")
    def check_permission(self, event):
        return self._assert(
            self._has_permission(
                event["server"], event["user"], event["request_args"][0]
            )
        )

    @utils.hook("check.command.authenticated")
    def check_authenticated(self, event):
        return self._assert(self._is_identified(event["server"], event["user"]))
