from mod_base import *

class View(Command):
    """View various bot information."""

    def GetAuthedUsers(self):
        users = []
        for user in self.bot.users:
            if user.IsAuthed():
                users.append(user)
        return users
    
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if args:
            if args[0] == "lsw":
                winnames = []
                for w in self.bot.windows:
                    winnames.append(w.GetName())
                winnames.sort()
                win.Send(", ".join(winnames))
            elif args[0] == "lsu":
                nicks = []
                for u in self.bot.users:
                    nicks.append(u.GetNick())
                nicks.sort()
                win.Send(", ".join(nicks))
            elif args[0] == "auths":
                auths = self.GetAuthedUsers()
                if not auths:
                    win.Send("nobody has authed")
                    return True
                s = ""
                for u in auths:
                    s += u.GetNick() + "[" + u.account["name"] + "] "
                win.Send(s)
        else:
            win.Send("use: lsw, lsu, lsa")

module = {
    "class": View,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH
}