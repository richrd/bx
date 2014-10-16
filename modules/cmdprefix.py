from mod_base import *

class CmdPrefix(Command):
    """Check or set the command prefix that the bot will respond to."""
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if args.Empty():
            cp = self.bot.config["cmd_prefix"]
            win.Send("current command prefix is: " + cp)
            return False
        self.bot.config["cmd_prefix"] = args[0]
        win.Send("done")

module = {
    "class": CmdPrefix,
    "type": MOD_COMMAND,
    "level": 5,
    "zone": IRC_ZONE_BOTH
}