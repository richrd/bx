from mod_base import *

class CmdPrefix(Command):
    """Set the command prefix that the bot will respond to."""
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if args.Empty():
            win.Send("specify prefix to use for detecting commands")
            return False
        self.bot.config["cmd_prefix"] = args[0]
        win.Send("done")

module = {
    "class": CmdPrefix,
    "type": MOD_COMMAND,
    "level": 5,
    "zone": IRC_ZONE_BOTH
}