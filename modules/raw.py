from mod_base import*

class Raw(Command):
    """Send raw data to the irc server."""
    def run(self, win, user, data, caller=None):
        if data == None:
            return False
        self.bot.SendRaw(data)
        return True

module = {
    "class": Raw,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH
}