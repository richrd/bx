from mod_base import*

class AddAccount(Command):
    """Create a new account.

    Usage: addaccount name password password
    """
    def run(self, win, user, data, caller=None):
        args = self.args
        if len(args) < 3:
            win.Send("Please provide account name, and password twice.")
            return False
        account_name = args[0].lower()
        
        if self.bot.config.AccountExists(account_name):
            win.Send("An account with that name already exists!")
            return False
        if args[1] != args[2]:
            win.Send("Sorry, those passwords don't match!")
            return False

        self.bot.config.AddAccount(account_name,args[1])
        win.Send("Account created!")
        return True

module = {
    "class": AddAccount,
    "type": MOD_COMMAND,
    "level": 5,
    "zone": IRC_ZONE_QUERY,
}