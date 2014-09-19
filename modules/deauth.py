from mod_base import*

class Deauth(Command):
    """Logout of the bot."""
    def run(self, win, user, data, caller=None):
        if user.Deauth():
            win.Send("you are no longer authed.")
            return True
        else:
            win.Send("you haven't authed yet.")
            return False

module = {
    "class": Deauth,
    "type": MOD_COMMAND,
    "level": 0,
    "zone":IRC_ZONE_BOTH,
}