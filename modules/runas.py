from mod_base import*

class RunAs(Command):
    """Run a command as another user."""
    def run(self,win,user,data,caller=None):
        args = Args(data)
        if len(args)<2:
            win.Send("provide at least nick, command")


        target_user = False
        for u in self.bot.users:
            if u.GetNick()==args[0]:
                target_user = u
                break;

        if not target_user:
            target_user=self.bot.FindUser(args[0])
            
        if not target_user:
            win.Send("user not found")
            return False

        cmd=args[1]
        arg = None
        if len(args)>2:
            arg = " ".join(args[2:])

        inst = self.bot.GetCommand(cmd)
        if not inst:
            win.Send("no such command")
            return False
        if inst.zone == IRC_ZONE_QUERY:
            status = inst.run(target_user.GetQuery(),target_user,arg,caller=user)
        else:
            status = inst.run(win,target_user,arg,caller=user)

module = {
    "class": RunAs,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH
}