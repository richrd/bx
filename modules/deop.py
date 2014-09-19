from mod_base import*

class TakeOP(Command):
    """Take OPs from a nick."""
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if data != None:
            users = []
            for arg in args:
                user = self.bot.FindUser(arg)
                if user == False:
                    continue
                if win.HasUser(user):
                    users.append(user)

            if users != []:
                win.TakeUserModes(users, IRC_MODE_OP)
            else:
                win.Send("invalid nicks")

module = {
    "class": TakeOP,
    "type": MOD_COMMAND,
    "level": 2,
    "zone":IRC_ZONE_BOTH,
}