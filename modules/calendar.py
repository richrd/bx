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
        timestamp = time.strftime('%d.%m.%Y %H:%M', time.gmtime(t))
        return timestamp

    def entry_to_str(self, name, entry):
        timestamp = self.time_to_str(entry['utime'])
        return '[' + name + '] ' + timestamp + ' ' + entry['description']

    def current_events(self, win):
        if not self.cal_events:
            win.Send('No events.')
            return False
        for key in self.cal_events.keys():
            entry = self.cal_events[key]
            win.Send(self.entry_to_str(key, entry))

    def add_event(self, name, entry):
        self.cal_events[name] = entry
        self.storage.Store()
        return True

    def remove_event(self, name):
        if name in self.cal_events.keys():
            del self.cal_events[name]
            self.storage.Store()
            return True
        return False

    def get_event(self, name):
        if name in self.cal_events.keys():
            event = self.cal_events[name]
            return event
        return False

    def event(self, event):
        pass

    def run(self, win, user, data, caller = None):
        args = Args(data)
        if args.Empty():
            self.current_events(win)
            return False
        elif len(args) == 1:
            name = args[0].lower()
            if name[0] == '-':
                name = name[1:]
                if self.remove_event(name):
                    win.Send('Event removed.')
                    return True
                win.Send('No event with that name.')
                return False
            e = self.get_event(name)
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
            self.add_event(name, entry)
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
