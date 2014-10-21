from mod_base import *

class CmdSeparator(Command):
    """Check or set the command seperator."""
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if args.Empty():
            cp = self.bot.config["cmd_separator"]
            win.Send("current command separator is: " + cp)
            return False
        self.bot.config["cmd_separator"] = args[0]
        win.Send("done")

module = {
    "class": CmdSeparator,
    "type": MOD_COMMAND,
    "level": 5,
    "zone": IRC_ZONE_BOTH
}