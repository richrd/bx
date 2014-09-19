from mod_base import*

class GainOP(Command):
    """Have the bot request OPs from QuakeNet (if channel has no OPs)."""
    def run(self, win, user, data, caller=None):
        self.bot.Privmsg("R","requestop " + win.GetName())

module = {
    "class": GainOP,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH,
}