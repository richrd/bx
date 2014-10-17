# -*- coding: utf-8 -*-
from mod_base import * 

class CLI(Listener):
    """A command line interface for the bot. Activate with CTRL+C in console."""
    def init(self):
        self.events = [IRC_EVT_INTERRUPT, IRC_EVT_MSG]

    def override_cmd(self, cmd, data):
        if cmd == "output":
            if not len(data):
                self.bot.log.Info("cmd", "Specify log domain to +show or -hide.")
                return False
            arg = data.lower()
            opt = arg[0]
            domain = arg[1:]
            domains = self.bot.config["log_domains"]
            if opt == "-" and domain in domains:
                domains.pop(domains.index(domain))
                self.bot.log.Info("mod", "domain removed")
            elif opt == "-":
                self.bot.log.Info("mod", "domain not currently enabled")
            elif opt == "+" and domain in domains:
                self.bot.log.Info("mod", "domain already exists")
            elif opt == "+" and not domain in domains:
                domains.append(domain)
                self.bot.log.Info("mod", "domain added")
            return True
        elif cmd == "reprint":
            self.bot.log.RenderAll()
            return True
        return False

    def run_cmd(self, data):
        args = Args(data)
        cmd = args[0]
        data = args.Range(1) or None
        if not self.override_cmd(cmd, data):
            self.bot.RunCommand(cmd, self.bot.GetWindow(self.bot.me.GetNick()), self.bot.admin, data)

    def handle_input(self, data):
        self.run_cmd(data)

    def interrupt(self, event):
        try:
            inp = raw_input("CTRL+C to exit, ENTER to continue:")
            inp = inp.decode("utf8")
            self.handle_input(inp)
            return True
        except KeyboardInterrupt:
            return False
        return True

    def event(self, event):
        if event.type == IRC_EVT_INTERRUPT:
            return self.interrupt(event)
        elif event.type == IRC_EVT_MSG:
            if event.win == self.bot.GetWindow(self.bot.me.GetNick()):
                self.bot.log.Info("cmd", event.msg)
                return True
module = {
    "class": CLI,
    "type": MOD_LISTENER,
    "zone": IRC_ZONE_BOTH,
}
