from mod_base import*

class DelChan(Command):
    """Remove a channel from the autojoin list."""
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if args.Empty():
            win.Send("specify channel to delete from autojoin list")
            return False
        if self.bot.IsChannelName(args[0]):
            if self.bot.config.RemoveChannel(args[0]):
                win.Send("channel removed")
                return True
            win.Send("channel doesn't exists")
        else:
            win.Send("invalid channel name")

module = {
    "class": DelChan,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH
}