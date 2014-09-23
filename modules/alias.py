from mod_base import *

class Alias(Command):
    """Defines a new command alias.

    Usage: alias new_name command
    """

    def run(self, win, user, data, caller=None):
        args = Args(data)
        if len(args) < 2:
            win.Send("please provide new alias and command")
            return False

        alias = args[0].lower()
        cmd = args[1].lower()

        if not cmd in self.bot.commands.keys():
            win.Send("that command doesn't exist")
            return False

        # Move to config.py
        if not cmd in self.bot.config["modules"].keys():
            self.bot.config["modules"][cmd] = {"aliases":[alias]}
        else:
            if not "aliases" in self.bot.config["modules"][cmd].keys():
                self.bot.config["modules"][cmd]["aliases"] = [alias]
            elif alias not in self.bot.config["modules"][cmd]["aliases"]:
                self.bot.config["modules"][cmd]["aliases"].append(alias)

        self.bot.config.LoadAliases()
        win.Send("done")

module = {
    "class": Alias,
    "type": MOD_COMMAND,
    "level": 5,
}
