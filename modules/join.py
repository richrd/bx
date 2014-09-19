from mod_base import*

class Join(Command):
    """Join list of channels, or rejoin the current channel if no channels are given."""
    def run(self,win,user,data,caller=None):
        args = Args(data)
        if not args:
            self.bot.PartChannels([win.GetName()])
            self.bot.JoinChannels([win.GetName()])
            return True
        self.bot.JoinChannels(args)
        return True

module = {
    "class": Join,
    "type": MOD_COMMAND,
    "level": 2,
    "zone":IRC_ZONE_BOTH,
    "aliases":["j"]
}