from mod_base import*

class Exc(Command):
    """Execute python code."""
    def run(self, win, user, data, caller=None):
        try:
            exec(data)
            return True
        except Exception,e:
            win.Send("fail: "+str(e))
        return False

module = {
    "class": Exc,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH
}