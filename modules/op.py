from mod_base import*

class GiveOP(Command):
    """Give OPs to yourself (default), or a list of nicks, or everyone (with '*')."""
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if "*" in args:
            users = win.GetUsers()      # FIXME: drop unneccesary nicks
            win.GiveUserModes(users,IRC_MODE_OP)
        else:
            if data == None:
                win.GiveUserModes([user],IRC_MODE_OP)
            else:
                users = []
                for arg in args:
                    user = self.bot.FindUser(arg)
                    if user == False:continue
                    if win.HasUser(user):users.append(user)
                if users != []:
                    win.GiveUserModes(users,IRC_MODE_OP)
                else:
                    win.Send("invalid nicks")

module = {
    "class": GiveOP,
    "type": MOD_COMMAND,
    "level": 2,
    "zone":IRC_ZONE_BOTH,
}