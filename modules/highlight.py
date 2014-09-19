from mod_base import*

class HighlightAll(Command):
    """Highlight everyone on the current channel."""
    def run(self, win, user, data, caller=None):
        my_nick = self.bot.me.GetNick()
        nicks = win.GetNicks()

        if my_nick in nicks:
            nicks.pop(nicks.index(my_nick))
        if user.GetNick() in nicks:
            nicks.pop(nicks.index(user.GetNick()))

        win.Send(" ".join(nicks))

module = {
    "class": HighlightAll,
    "type": MOD_COMMAND,
    "level": 1,
    "zone": IRC_ZONE_BOTH,
    "throttle": 600,
    "aliases": ["hl"]
}