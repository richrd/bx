from mod_base import*

class UserInfo(Command):
    """View info about you or another nick."""
    def run(self,win,user,data,caller=None):
        args = Args(data)
        u = user
        if len(args)>0:
            result = self.bot.FindUser(args[0])
            if result!=False:
                u = result
            else:
                win.Send("user not found")
                return False

        ui = u.GetNick()+" "+u.hostname

        if u.IsOnline():
            ui += ", [online]"
        else:
            ui += ", [offline]"

        ui += ", active: "+time_stamp_numeric(u.last_active)
        
        if u.IsAuthed():
            ui += ", authed as "+u.account["name"]
        
        ui += "\n"
        chans = []
        for chan in u.Channels():
            pre = ""
            if chan.UserHasMode(u,IRC_MODE_VOICE):
                pre = "+"
            if chan.UserHasMode(u,IRC_MODE_OP):
                pre = "@"
            chans.append(pre+chan.GetName())

        user.Send(ui)
        if chans:
            user.Send( "at: "+(" ".join(chans)) )

module = {
    "class": UserInfo,
    "type": MOD_COMMAND,
    "level": 1,
    "zone":IRC_ZONE_BOTH,
}