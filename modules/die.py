from mod_base import*

class Die(Command):
    """Kill the bot."""
    def run(self,win,user,data,caller=None):
        win.Send("dying...")
        self.bot.StopBot()

module = {
    "class": Die,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH
}