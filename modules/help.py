from mod_base import *

class Help(Command):
    """Provide basic instructions on using the bot."""

    def run(self, win, user, data, caller=None):
        """Display information about a specific command."""
        if not data:
            self.general_help(user)
        else:
            cmd = self.bot.GetCommand(data)
            if cmd:
                win.Send(cmd.GetMan())
            else:
                win.Send("i don't know that command")

    def general_help(self, user):
        """Display general help."""
        lines = [
            "You can run commands by typing a '"+self.bot.config["cmd_prefix"]+"' at the beginning of a message.",
            "To see what commands are available use 'cmds'",
            "and to see what a command does, use 'help command'.",
            "You can login with 'auth' and logout with 'deauth'.",
            "To check your permission level, use 'perm'.",
            "To ask me to remember your account, use 'trustme'.",
            "Check out the code @ github: https://github.com/richrd/bx",
            "Peace.",
            ]
        for line in lines:
            user.Privmsg(line)

module = {
    "class": Help,
    "type": MOD_COMMAND,
    "level": 0,
    "zone":IRC_ZONE_BOTH,
    "throttle":60
}