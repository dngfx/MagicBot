#--depends-on commands

import re, random, pydig
from src import ModuleManager, utils

ALLOWED_RECORDS = ["A", "AAAA", "NS", "MX", "TXT", "CNAME", "SOA"]


class Module(ModuleManager.BaseModule):

    @utils.hook("received.command.dig")
    @utils.kwarg("help", "Return domain records according to type")
    @utils.spec("!<domain>word !<record>word")
    def dig(self, event):
        domain = event["spec"][0]
        record = event["spec"][1].upper()

        if record not in ALLOWED_RECORDS:
            types = ", ".join(ALLOWED_RECORDS)
            event["stderr"].write("Unrecognised record type (%s) — Allowed record types are: %s" % (record, types))
            return

        dig = pydig.query(domain, record)
        dig_formatted = ", ".join(dig)
        if not dig:
            dig_formatted = utils.irc.color(utils.irc.bold("[No Record]"), utils.consts.RED)

        event["stdout"].write("%s Record for %s: %s" % (utils.irc.bold(record), utils.irc.bold(domain), dig_formatted))
