from mod_base import*

class Evl(Command):
    """Evaluate a python expression."""
    def run(self,win,user,data,caller=None):
        try:
            result = str(eval(data))
            win.Send(result)
            return True
        except Exception,e:
            win.Send("fail:"+str(e))
        return False

module = {
    "class": Evl,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH
}