from mod_base import*

class AddChan(Command):
    """Add a channel to the autojoin list."""
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if args.Empty():
            win.Send("specify channel to add to autojoin list")
            return False
        if self.bot.IsChannelName(args[0]):
            if self.bot.config.AddChannel(args[0]):
                win.Send("channel added")
                return True
            win.Send("channel already exists")
        else:
            win.Send("invalid channel name")

module = {
    "class": AddChan,
    "type": MOD_COMMAND,
    "level": 5,
    "zone": IRC_ZONE_BOTH
}