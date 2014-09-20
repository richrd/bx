from mod_base import *

class Kick(Command):
    """Kick a user off a channel. Usage: kick [#channel] nick"""

    def run(self, win, user, data, caller=None):
        args = Args(data)
        if args.Empty():
            win.Send("kick who?")
            return
        if args.HasType("channel"):
            win = self.bot.GetWindow(args.Take("channel"), False) or win
        elif win.zone == IRC_ZONE_QUERY:
            win.Send("specify channel to kick from")
            return False
        target = self.bot.FindUser(args[0])
        if target:
            win.Kick(target)

module = {
    "class": Kick,
    "type": MOD_COMMAND,
    "level": 2,
}
