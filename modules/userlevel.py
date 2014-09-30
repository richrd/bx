from mod_base import*

class UserLevel(Command):
    """Change the permission level of a user.

    Usage: userlevel user level
    """
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if len(args) < 2:
            win.Send("specify user and level to set")
            return False
        name = args[0].lower()
        target = self.bot.FindUser(name)
        if not target:
            win.Send("Sorry, can't find that user")
            return False

        try:
            level = int(args[1])
        except:
            win.Send("Invalid value for level. Must be an integer number.")
            return False
        self.bot.config.UserSet(name, "level", level)
        win.Send("done")
        return True

module = {
    "class": UserLevel,
    "type": MOD_COMMAND,
    "level": 5,
    "zone": IRC_ZONE_BOTH
}