from mod_base import *

class Define(Command):
    """Define terms and words related to the bot."""
    def init(self):
        self.glossary = {
            "auth": "Authenticate or login to the bot. You need a username and password.",
            "level": "Level is a number indicating what permissions a user has. A higher number indicates more permissions.",
            "module": "Modules are individual components of the bot that add extra features.",
            "command": "Commands are used to tell the bot to do various things.",
        }

    def run(self, win, user, data, caller=None):
        data = "" if not data else data.lower()
        if data in self.glossary.keys():
            win.Send(self.glossary[data])
        else:
            win.Send("I don't know anything about that")

module = {
    "class": Define,
    "type": MOD_COMMAND,
    "level": 0,
}