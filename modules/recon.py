from mod_base import*

class ReloadConfig(Command):
    """Reload bot config."""
    def run(self, win, user, data, caller=None):
        fname = self.bot.config.filename # FIXME seperate config module and config file loading
        result1 = self.bot.ReloadConfig()
        self.bot.config.filename = fname
        result2 = self.bot.config.Load()
        if result1 and result2:
            win.Send("reloaded config")
            return True
        else:
            win.Send("failed to reload config: " + str(result))
            return False

module = {
    "class": ReloadConfig,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH
}