from mod_base import*

class Mod(Command):
    """View or modify enabled modules (commands & listeners).

    Usage: mod [-/+]module_name
    e.g. prefix module name with - or + for disable or enable
    """
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if len(args) == 0:
            win.Send("current mods: " + (" ".join(self.bot.config["default_mods"])))
            win.Send("to add or remove, use +/-modulename")
            return

        val = args[0]
        if val[0] == "-":
            val = val[1:]
            self.bot.config.DisableMod(val)
            self.bot.ReloadModules()
            win.Send("disabled module '" + val + "'")

        else:
            if val[0] == "+":
                val = val[1:]
            self.bot.config.EnableMod(val)
            self.bot.ReloadModules()
            win.Send("enabled module '" + val + "'")

module = {
    "class": Mod,
    "type": MOD_COMMAND,
    "level": 5,
    "zone": IRC_ZONE_BOTH
}