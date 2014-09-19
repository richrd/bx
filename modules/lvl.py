from mod_base import*

class Lvl(Command):
    """View your permission level (or someone elses)."""
    def run(self,win,user,data,caller=None):
        args = Args(data)
        if len(args)==0:
            perm = user.GetPermission()
            win.Send(str(perm))
        else:
            user = self.bot.FindUser(args[0])
            if user:
                perm = user.GetPermission()
                win.Send(str(perm))
            else:
                win.Send("user not found")

module = {
    "class": Lvl,
    "type": MOD_COMMAND,
    "level": 0,
    "zone":IRC_ZONE_BOTH,
}