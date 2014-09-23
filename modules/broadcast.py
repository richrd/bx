from mod_base import *

class Broadcast(Hybrid):
    """Broadcast messages or command out put to channels and/or users.

    Usage: broadcast [+-]name [channel,channel,...] [command] [args]
    """
    def init(self):
        self.events = [IRC_EVT_INTERVAL]
        self.broadcasts = {}

    def event(self, event):
        for name in self.broadcasts.keys():
            broadcast = self.broadcasts[name]
            if not broadcast["last_exec"]:
                self.RunBroadcast(broadcast)
            elif time.time()-broadcast["last_exec"] > broadcast["interval"]:
                self.RunBroadcast(broadcast)

    def RunBroadcast(self, broadcast):
        broadcast["last_exec"] = time.time()
        cmd = self.bot.GetCommand(broadcast["cmd"])
        win = self.bot.GetWindow(broadcast["targets"])
        cmd.run(win, self.bot.me, broadcast["cmd_args"])

    def run(self, win, user, data, caller=None):
        args = Args(data)
        hint = "provide [+-]action, targets, interval and command"
        if args.Empty():
            win.Send(hint)

        name = args[0]
        if name[0] == "-":
            if self.RemoveBroadcast(name[1:]):
                win.Send("broadcast removed")
                return True
            win.Send("no broadcast with that name")
            return False

        if name[0] == "+":
            name = name[1:]

        if len(args) < 4:
            win.Send(hint)
            return False

        targets = args[1]
        interval = str_to_seconds(args[2])
        if not interval:
            win.Send("invalid interval")
            return False

        cmd = args[3]
        cmd_args = ""
        if len(args) > 3:
            cmd_args = args.Range(4)

        command = self.bot.GetCommand(cmd)
        if not command:
            win.Send("cmd does not exists")
            return False

        if command.level > user.GetPermission():
            win.Send("sry, you can't add that command")
            return False

        self.AddBroadcast(name, targets, interval, cmd, cmd_args)
        win.Send("broadcast added")
        return True

    def AddBroadcast(self, name, targets, interval, cmd, cmd_args):
        broadcast = {
            "targets": targets,
            "interval": interval,
            "cmd": cmd,
            "cmd_args": cmd_args,
            "last_exec": None,
        }
        self.broadcasts[name] = broadcast

    def RemoveBroadcast(self, name):
        if name in self.broadcasts.keys():
            del self.broadcasts[name]
            return True
        return False

module = {
    "class": Broadcast,
    "type": MOD_BOTH,
    "level": 2,
    "zone": IRC_ZONE_BOTH,
    "interval": 1,
}