from mod_base import*

class Part(Command):
    """Part list of channels."""
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if not args: args = [win.GetName()]
        self.bot.PartChannels(args)

module = {
    "class": Part,
    "type": MOD_COMMAND,
    "level": 2,
    "zone":IRC_ZONE_CHANNEL,
    "aliases":["p"]
}