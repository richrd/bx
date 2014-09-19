from mod_base import*

class OnJoin(Listener):
    def init(self):
        self.events = [IRC_EVT_CHAN_JOIN]
        
    def event(self,event):
        cmd = self.bot.GetCommand("tell")
        if cmd!= False:cmd.OnOnline(event.user)

module = {
    "class": OnJoin,
    "type": MOD_LISTENER,
    "zone":IRC_ZONE_CHANNEL
}