from mod_base import*

class QAuth(Listener):
    """Automatically auth with Q @ QuakeNet when connecting to IRC."""
    def init(self):
        self.events = [IRC_EVT_READY]

    def event(self,event):
        if not "q_auth" in self.bot.config.keys(): return False
        u, p = self.bot.config["q_auth"]
        self.bot.Privmsg("q@cserve.quakenet.org","auth " + u + " " + p)
        self.bot.SendRaw("MODE " + self.bot.me.GetNick() + " +x")

module = {
    "class": QAuth,
    "type": MOD_LISTENER,
    "zone": IRC_ZONE_BOTH,
}