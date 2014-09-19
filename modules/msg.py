from mod_base import*

class Msg(Command):
    """Send a message as the bot to a user or channel."""
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if len(args) < 2:
            win.Send("provide destination and message")
            return False
        self.bot.Privmsg(args[0], args.Range(1,))
        return True

module = {
    "class": Msg,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH
}