from mod_base import*

class ReloadMods(Command):
    """Reload bot modules."""
    def run(self, win, user, data, caller = None):
        result = self.bot.ReloadModules()
        if result == True:
            win.Send("reloaded modules")
            return True
        else:
            win.Send("failed to reload modules: "+str(result))
            return False

module = {
    "class": ReloadMods,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH,
}