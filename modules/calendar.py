from mod_base import *

class Calendar(Hybrid):
    """Calendar. Add and remove calendar entrys. Also sends notifications about future calendar entrys.

    Usage: calendar +meeting 29.10.2014 17:00 description
    Usage: calendar -meeting
    """
    
    def init(self):
        self.events = [IRC_EVT_INTERVAL]
        self.cal_entrys = {}

    def event(self, event):
        for name in self.cal_entrys.keys():
            entry = self.cal_entrys[name]
            # do something

    def run(self, win, user, data, caller=None):
        args = Args(data)
        hint = "provide [+-]action, targets, interval and command"
        if args.Empty():
            # List events or give help here
            win.Send("Add or remove an event.")
            return False

        if len(args) == 1:
            # Remove event
            name = args[0]
        else.
            # Add event
            name = args[0]
            date = args[1]
            stime = args[2]
            description = args.Range(3)
            # Add it

module = {
    "class": Calendar,
    "type": MOD_BOTH,
    "level": 0,
    "zone": IRC_ZONE_BOTH,
    "interval": 60,
    "aliases": ["cal"],
}