from mod_base import*

class Cmds(Command):
    """Lists the commands you can use."""
    def run(self, win, user, data, caller=None):
        cmds = self.bot.GetCommandsByPermission(user.GetPermission())
        cmds.sort()
        win.Send("commands available to you: "+(", ".join(cmds)))

module = {
    "class": Cmds,
    "type": MOD_COMMAND,
    "level": 0,
    "zone":IRC_ZONE_BOTH,
}