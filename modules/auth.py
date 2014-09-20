from mod_base import*

class Auth(Command):
    """Identify yourself with the bot (login). Usage: auth <user> <pass>"""
    def run(self, win, user, data, caller=None):
        if user.IsAuthed():
            win.Send("you've already authed")
            return False
        args = Args(data)
        if len(args) < 2:
            win.Send("please give a username and password (auth user pass)")
        else:
            if self.bot.AuthenticateUser(user,args[0], args[1]):
                win.Send("authed! you are now level " + str(user.GetPermission()) + ". use 'deauth' to log out.")
            else:
                win.Send("wrong username or password!")

module = {
    "class": Auth,
    "type": MOD_COMMAND,
    "level": 0,
    "zone": IRC_ZONE_QUERY,
}