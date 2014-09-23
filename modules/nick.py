from mod_base import*

class Nick(Command):
    """Change the nick of the bot."""
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if len(args) == 1:
            self.bot.me.Nick(args[0])
            self.bot.config["nicks"] = [args[0]]
        else:
            win.Privmsg("nick can't contain spaces")
            return False

module = {
    "class": Nick,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH
}
