from mod_base import*

class AutoOP(Listener):
    def init(self):
        self.events = [IRC_EVT_USER_AUTHED, IRC_EVT_CHAN_JOIN, IRC_EVT_CHAN_USER_MODE_CHANGE]
        
    def event(self, event):
        if event.id == IRC_EVT_CHAN_JOIN:
            if event.user.IsAuthed():
                if self.bot.me.HasOP(event.win):
                    event.win.GiveUserModes([event.user], IRC_MODE_OP)

        if event.id == IRC_EVT_CHAN_USER_MODE_CHANGE:
            if event.user == self.bot.me:
                if self.bot.me.HasOP(event.win):
                    users = []  # List of users to op
                    for user in event.win.GetUsers():
                        if user.IsAuthed(): # Add all authed users to list
                            users.append(user)
                    event.win.GiveUserModes(users, IRC_MODE_OP)

        if event.id == IRC_EVT_USER_AUTHED:
            for win in event.user.Channels():
                if self.bot.me.HasOP(win):
                    win.GiveUserModes([event.user], IRC_MODE_OP)

module = {
    "class": AutoOP,
    "type": MOD_LISTENER,
}