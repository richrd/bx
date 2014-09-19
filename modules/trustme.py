from mod_base import*

class Trust(Command):
    """Remember your account. Connects your current hostname to your account so you don't have to auth every time you connect."""
    def IsPermittedHostname(self,hostname):
        end = hostname.split("@")[1]
        blocked = ["mobile", "gprs"]
        for b in blocked:
            if end.find(b) != -1:
                return False
        return True
    
    def run(self, win, user, data, caller=None):
        args = Args(data)
        if not user.IsAuthed():
            win.Send("you need to be authed")
            return False

        if self.IsPermittedHostname(user.hostname):
            if self.bot.config.RememberAccountHostname(user.account["name"],user.hostname):
                win.Send("your account is now connected to the hostname: "+str(user.hostname)+".")
                win.Send("next time you connect with the same hostname you'll be automatically authed.")
            else:
                win.Send(user.GetNick()+": your current hostname is already remembered.")
        else:
            win.Send("sorry, your current hostname can't be trusted because it's dynamic (changes each time you connect).")

module = {
    "class": Trust,
    "type": MOD_COMMAND,
    "level": 0,
    "zone":IRC_ZONE_BOTH,
}