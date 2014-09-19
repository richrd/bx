from mod_base import*

class ClearLogs(Command):
    """Clear n. number of messages from window logs (or all if no arguments given)."""
    def run(self, win, user, data, caller=None):
        num = len(win.log)
        if data != None:
            try:
                num = int(data)
            except:
                win.Send("invalid argument, must be 1-" + str(num))
                return False
            
        i = 0
        while i <= num:
            try:
                win.log.pop(-1)
            except:
                break
            i += 1
        win.Send("cleared " + str(i) + " messages.")

module = {
    "class": ClearLogs,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH,
}