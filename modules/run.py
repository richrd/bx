from mod_base import*

class Run(Command):
    """Run a command as another user (and/or on another channel). Usage: [channel] user command"""
    def run(self, win, user, data, caller=None):
        args = Args(data)
        target_win = win
        if len(args) < 2:
            win.Send("provide at least nick, command")
        if len(args) > 2:
            if args.IsChannel(args[0]):
                new_win = self.bot.GetWindow(args[0], create=False)
                if new_win:
                    target_win = new_win
                    args.Drop(0) # Remove the channel argument from the argument list
                else:
                    win.Send("Can't find that channel.")
                    return False

        target_user = self.bot.FindUser(args[0])
        self.Log("mod", "arg0:" + str(args[0]) + " user:" + str(target_user))
            
        if not target_user:
            win.Send("user not found")
            return False

        cmd = args[1]
        arg = None
        if len(args) > 2:
            arg = " ".join(args[2:])

        inst = self.bot.GetCommand(cmd)
        if not inst:
            win.Send("no such command")
            return False
        if inst.zone == IRC_ZONE_QUERY:
            status = inst.run(target_user.GetQuery(), target_user, arg, caller=user)
        else:
            status = inst.run(target_win, target_user, arg, caller=user)

module = {
    "class": Run,
    "type": MOD_COMMAND,
    "level": 5,
    "zone":IRC_ZONE_BOTH
}