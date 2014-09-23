from mod_base import*

class AutoChanMode(Listener):
    """Automatically manage channel modes according to config."""
    def init(self):
        self.events = [
                        IRC_EVT_CHAN_USER_MODE_CHANGE,
                        IRC_EVT_CHAN_MODE_CHANGE,
                        ]
        self.all_modes = "cCDilmMnNoprstTuv"
        
    def RepairModes(self, event):
        if event.id == IRC_EVT_CHAN_MODE_CHANGE and event.user == self.bot.me:
            return False
        valid = self.bot.config.GetChannelModes(event.win)
        if valid == None:
            return False

        del_modes = self.all_modes
        for mode in valid:
            del_modes = del_modes.replace(mode, "")
        event.win.SetModes("-" + del_modes)
        event.win.SetModes(valid)

    def event(self, event):
        m = self.bot.config.GetChannelModes(event.win)
        if m == None:
            return False

        if event.id == IRC_EVT_CHAN_MODE_CHANGE:
            if self.bot.me.HasOP(event.win):
                self.RepairModes(event)

        if event.id == IRC_EVT_CHAN_USER_MODE_CHANGE:
            if event.user == self.bot.me:
                if self.bot.me.HasOP(event.win):
                    self.RepairModes(event)

module = {
    "class": AutoChanMode,
    "type": MOD_LISTENER,
}