from mod_base import *

class AutoReJoin(Listener):
    """Automatically rejoin a channel after kick."""
    def init(self):
        self.events = [IRC_EVT_CHAN_KICK]

    def event(self, event):
        print event
        print self.bot.me
        print event.user
        if event.user.GetNick() == self.bot.me.GetNick():
            print "REJOIN"
            self.bot.Join(event.win.GetName())

module = {
    "class": AutoReJoin,
    "type": MOD_LISTENER,
}