from mod_base import*

class Nick(Hybrid):
    """Change the nick of the bot. If nick isn't available, the nick will be reclaimed when it becomes available."""
    def init(self):
        self.events = [IRC_EVT_INTERVAL, IRC_EVT_USER_NICK_CHANGE, IRC_EVT_USER_QUIT]

    def event(self, event):
        desired = self.bot.config["nicks"][0]
        if event.type == IRC_EVT_INTERVAL:
            if self.bot.me.nick != desired:
                self.ReclaimNick()
        elif event.type == IRC_EVT_USER_QUIT:
            if event.user.GetNick() == desired:
                self.ReclaimNick()
        elif event.type == IRC_EVT_USER_NICK_CHANGE:
            if event.user.GetNick() == desired:
                self.ReclaimNick()

    def run(self, win, user, data, caller=None):
        args = Args(data)
        if len(args) == 1:
            self.bot.me.Nick(args[0])
            self.bot.config["nicks"] = [args[0]]
        else:
            win.Privmsg("nick can't contain spaces")
            return False

    def ReclaimNick(self):
        self.bot.me.Nick(self.bot.config["nicks"][0])

module = {
    "class": Nick,
    "type": MOD_BOTH,
    "level": 5,
    "zone": IRC_ZONE_BOTH,
    "interval": 60*10,
}
