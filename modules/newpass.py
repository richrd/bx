from mod_base import*

class NewPass(Command):
    """Change your password.

    Usage: newpass oldpassword newpassword newpassword
    """
    def run(self,win,user,data,caller=None):
        args = self.args
        if not args or len(args)<3:
            win.Send("Usage: newpass oldpassword newpassword newpassword")
            return False

        if not user.IsAuthed():
            win.Send("you've not logged in")
            return False

        oldpass, pass1, pass2 = args[0:3]

        if pass1 == pass2:
            if self.config.ChangeAccountPass(user.account["name"], oldpass, pass1):
                win.Send("password changed!")
            else:
                win.Send("failed to change password! make sure your old password is correct.")
        else:
            win.Send("your new password didn't match up")

module = {
    "class": NewPass,
    "type": MOD_COMMAND,
    "level": 0,
    "zone":IRC_ZONE_QUERY,
}