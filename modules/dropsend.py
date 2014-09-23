from mod_base import *

class DropSend(Command):
    """Clear the outgoing message buffer. Warning: removes all data queued for sending to the IRC server."""
    def run(self, win, user, data, caller=None):
        self.bot.DropSendBuffer()
        win.Send("done")

module = {
    "class": DropSend,
    "type": MOD_COMMAND,
    "level": 5,
    "zone": IRC_ZONE_BOTH
}