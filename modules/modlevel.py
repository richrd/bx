from mod_base import*

class ModuleLevel(Command):
    """Change the permission level of a module.

    Usage: modlevel mod level
    """
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if len(args) < 2:
            win.Send("specify module and level to set")
            return False
        name = args[0].lower()
        mod = self.bot.GetModule(name)
        if not mod:
            win.Send("Sorry, can't find that module")
            return False

        try:
            level = int(args[1])
        except:
            win.Send("Invalid value for level. Must be an integer number.")
            return False
        self.bot.config.ModSet(name, "level", level)
        win.Send("done")
        return True

module = {
    "class": ModuleLevel,
    "type": MOD_COMMAND,
    "level": 5,
    "zone": IRC_ZONE_BOTH
}