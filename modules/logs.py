from mod_base import*

class Logs(Command):
    """Print channel logs. End sending with 'logs x'. Set time with e.g. 1h or 10m. Search logs with ?query (parameter starting with ?). Example: logs 2h ?hello"""
    def init(self):
        self.send_thread = None
        self.stop_thread = 0
        self.send_delay = 3
        self.target_user = None

        try:
            self.send_delay = self.bot.config["log_send_interval"]
        except:
            pass
        
    def get_logs(self, win, start_time, search=None):
        self.DebugCmd("get_logs(",win,start_time,")")
        logs = []
        
        total = len(win.log)
        msgs = list(win.log)

        if total == 0:
            return False

        i = 0
        while i < total:
            msg = msgs[i]
            i += 1
            if msg.time < start_time:   #only select messages in given timeframe
                continue
            if search != None:            #only select messages that match the search
                search = search.lower()
                if msg.nick.lower().find(search) == -1 and msg.text.lower().find(search) == -1: continue
            logs.append(msg)

        return logs

    def run(self, win, user, data, caller=None):
        try:
            self.run_wrapped(win, user, data, caller)
        except Exception, err:
            self.bot.log.Error("cmd", get_error_info())

    def run_wrapped(self, win, user, data, caller=None):
        max_age = 15*60
        log_win = win
        search = None

        args = Args(data)

        if args.FirstArg() == "x":
            self.stop_sending(user)
            win.Send("done")
            return True

        if args.HasType("duration"):
            max_age = args.Take("duration")

        if (caller and caller.GetPermission()>=5) or user.GetPermission()>=5:
            if args.HasType("channel"):
                log_win = self.bot.GetWindow(args.Take("channel"))

            if args.HasType("nick"):
                log_win = self.bot.GetWindow(args.Take("nick"))
        else:
            user.Privmsg("sry, that's not available")

        if args.HasType("search"):
            search = args.Take("search")

        msgs = self.get_logs(log_win, time.time()-max_age, search = search)

        if not msgs:
            win.Send("no logs")
            return False

        if self.is_sending():
            win.Send("sry, already pasting logs to somebody. end sending with 'logs x'")
            return False

        header = "["+log_win.GetName()+"] "
        if search != None:
            header += "(search:'"+search+"') "
        header += time_stamp_numeric(msgs[0].time) + ":"
        self.begin_sending(user, header, msgs)
        return True

    def is_sending(self):
        if self.send_thread != None:
            if s60:  # Legacy support
                return self.send_thread.isAlive()
            else:
                return self.send_thread.is_alive()
        return False
        
    def begin_sending(self, user, header, msgs):
        try:
            from threading import Thread
        except:
            user.Send("sorry, I don't support log pasting.")
            return False
        self.target_user = user
        self.send_thread = Thread(target = self.threaded_send, args = (user, header, msgs))
        self.send_thread.start()
        
    def threaded_send(self, user, header, msgs):
        user.Send(header)
        for msg in msgs:
            if self.stop_thread == 1:
                self.stop_thread = 0
                self.stopped(user)
                return False

            stamp = time_stamp_short(msg.time)
            line = stamp + " <" + msg.nick + "> " + msg.text

            user.Send(line)
            time.sleep(self.send_delay)
        self.end_send(user)

    def end_send(self, user):
        user.Send("end of logs")

    def stop_sending(self, user):
        self.stop_thread = 1
        
    def stopped(self, user):
        if user != self.target_user:
            user.Send("sry, log pasting was cancelled by someone")

module = {
    "class": Logs,
    "type": MOD_COMMAND,
    "level": 2,
    "zone":IRC_ZONE_BOTH,
}
