from mod_base import*

class Tell(Command):
    """Send a message to a user when they come online. Usage: tell <nick> <message>"""
    def init(self):
        self.queue = {}

    def run(self, win, user, data, caller=None):
        args = Args(data)
        if len(args) < 2:
            win.Send("provide nick and message")
            return False

        self.AddTell(user, args[0], args.Range(1))
        win.Send("Added message")
        return True

    def AddTell(self, user, search, message):
        arr = [search, time_stamp_short() + " <" + user.GetNick() + "> " + message]
        self.queue[time.time()]=arr

    def DoTell(self, user, key):
        entry = self.queue[key]
        user.Send(entry[1])
        del self.queue[key]

    def OnOnline(self, user):
        search = user.GetNick().lower()
        keys = self.queue.keys()
        keys.sort()
        for key in keys:
            entry = self.queue[key]
            if entry[0].find(search) != -1:
                self.DoTell(user, key)

module = {
    "class": Tell,
    "type": MOD_COMMAND,
    "level": 2,
    "zone":IRC_ZONE_BOTH
}