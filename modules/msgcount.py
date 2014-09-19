from mod_base import*

class MsgCount(Command):
    """Show the message log size of the current window."""    
    def run(self, win, user, data, caller=None):
        num = len(win.log)
        win.Send(str(num))

module = {
    "class": MsgCount,
    "type": MOD_COMMAND,
    "level": 2,
    "zone":IRC_ZONE_BOTH,
}