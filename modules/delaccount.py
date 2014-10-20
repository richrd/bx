from mod_base import *

class DelAccount(Command):
    """Permanently delete an existing account.

    Usage: delaccount username
    """
    def run(self, win, user, data, caller=None):
        args = self.args
        if args.Empty():
            win.Send("Please provide account to delete.")
            return False
        account_name = args[0].lower()
        
        if not self.bot.config.AccountExists(account_name):
            win.Send("That account doesn't exist.")
            return False

        self.bot.config.RemoveAccount(account_name)
        win.Send("Account deleted!")
        return True

module = {
    "class": DelAccount,
    "type": MOD_COMMAND,
    "level": 5,
    "zone": IRC_ZONE_BOTH,
}