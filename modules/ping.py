from mod_base import *

class Ping(Command):
    """Ping the bot, to make sure it's alive and kicking."""
    def run(self, win, user, data, caller=None):
        win.Send("pong, " + user.nick)

module = {
    "class": Ping,
    "type": MOD_COMMAND,
    "level": 0,
    "zone":IRC_ZONE_BOTH,
}