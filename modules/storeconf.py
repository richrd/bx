from mod_base import*

class StoreConf(Command):
    """Store configuration."""
    def run(self, win, user, data, caller=None):
        if self.bot.config.Store():
            win.Send("stored config")
        else:
            win.Send("failed to store config")

module = {
    "class": StoreConf,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH,
    "aliases":["sc"]
}