from mod_base import *

class Calendar(Hybrid):
    """Calendar. Add and remove calendar entrys. Also sends notifications about future calendar entrys.
    
    Usage: calendar +meeting 29.10.2014 17:00 description
    Usage: calendar -meeting
    """

    def init(self):
        self.events = [IRC_EVT_INTERVAL]
        self.storage.Load()
        self.cal_events = self.storage['entrys']

    def time_to_str(self, t):
        pass

    def entry_to_str(self, name, entry):
        timestamp = time.strftime('%d.%m.%Y %H:%M', time.gmtime(entry['utime']))
        return '[' + name + '] ' + timestamp + ' ' + entry['description']

    def CurrentEvents(self, win):
        if not self.cal_events:
            win.Send('No events.')
            return False
        for key in self.cal_events.keys():
            entry = self.cal_events[key]
            win.Send(self.entry_to_str(key, entry))

    def AddEvent(self, name, entry):
        self.cal_events[name] = entry
        self.storage.Store()
        return True

    def RemoveEvent(self, name):
        if name in self.cal_events.keys():
            del self.cal_events[name]
            self.storage.Store()
            return True
        return False

    def GetEvent(self, name):
        if name in self.cal_events.keys():
            event = self.cal_events[name]
            return event
        return False

    def event(self, event):
        pass

    def run(self, win, user, data, caller = None):
        args = Args(data)
        if args.Empty():
            self.CurrentEvents(win)
            return False
        elif len(args) == 1:
            name = args[0].lower()
            if name[0] == '-':
                name = name[1:]
                if self.RemoveEvent(name):
                    win.Send('Event removed.')
                    return True
                win.Send('No event with that name.')
                return False
            e = self.GetEvent(name)
            if e:
                win.Send(self.entry_to_str(name, e))
                return True
            win.Send('Event not found.')
            return False
        else:
            name = args[0].lower()
            if name[0] == '+':
                name = name[1:]
            date = args[1]
            stime = args[2]
            try:
                timestamp = time.strptime(date + ' ' + stime, '%d.%m.%Y %H:%M')
            except ValueError as e:
                win.Send('Invalid date or time, use format 31.12.2015 20:00.')
                return False

            timestamp = time.mktime(timestamp)
            description = args.Range(3)
            if name in self.cal_events.keys():
                win.Send('Event with that name already exists.')
                return False
            entry = {
                'utime': timestamp,
                'description': description
            }
            self.AddEvent(name, entry)
            win.Send('Event added.')
            return True


module = {
    'class': Calendar,
    'type': MOD_BOTH,
    'level': 0,
    'zone': IRC_ZONE_BOTH,
    'interval': 60,
    'aliases': ['cal'],
    'storage': {'entrys': {}}
}
