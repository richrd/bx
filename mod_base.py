# -*- coding: utf-8 -*-
"""mods.py: Modules for the IRC bot.

Contains all built in commands and listeners.

"""

import sys
import time
import traceback
from const import *

# Symbian S60 specific compatibility
s60 = False
if sys.platform == "symbian_s60":
    s60 = True
    sys.path.append("e:\\python")
    sys.path.append("c:\\python")
    sys.path.append("c:\\DATA\\python")

from helpers import *
from const import *


class Args:
    """Argument handler for commands."""
    def __init__(self, args=[], bot=None):
        self.bot = bot
        arg_list = []
        if type(args) != type([]):
            if args != None:
                arg_list = args.strip().split(" ")
        self.original = list(arg_list)
        self.args = list(arg_list)

    def __getitem__(self, item):
        return self.args[item]

    def __setitem__(self, item, value):
        self.original[item] = value

    def __len__(self):
        return len(self.args)

    def FirstArg(self):
        if len(self.original) != 0:
            return self.original[0]
        return ""

    def Empty(self):
        if len(self.args) == 0:
            return True
        return False

    def Range(self, start, end=None):
        if end == None:
            end = len(self.original)
        return (" ".join(self.original[start:end]))

    def Drop(self, what=0):              # drops a selected arg from list
        if type(what) == type(1):
            self.args.pop(what)
        else:
            self.args.pop(self.args.index(what))

    def IsStrSearch(sef, s):
        if s[0] != "?":return False
        return True

    def IsChannel(self, s):
        return s[0] in ["#", "&", "!"]

    def IsNick(self, s):
        return s[0] == "~"

    def IsAccount(self, name):
        return name in self.bot.config["accounts"].keys()

    def HasType(self, what):             # checks if a type is found in args
        return self.FindType(what)

    def Take(self, what):                # returns type matched
        return self.FindType(what, True)

    def FindType(self, what, commit=False):
        for arg in self.args:
            if what == "duration":
                val = str_to_seconds(arg)
                if val != False:
                    if commit:
                        self.Drop(arg)
                        return val
                    else:
                        return True
            elif what == "channel":
                if self.IsChannel(arg):
                    if commit:
                        self.Drop(arg)
                        return arg
                    else:
                        return True
            elif what == "search":
                if self.IsStrSearch(arg):
                    if commit:
                        self.Drop(arg)
                        return arg[1:]
                    else:
                        return True
            elif what == "nick":
                if self.IsNick(arg):
                    if commit:
                        self.Drop(arg)
                        return arg[1:]
                    else:
                        return True
            elif what == "account":
                if self.IsAccount(arg):
                    if commit:
                        self.Drop(arg)
                        return arg
                    else:
                        return True
        return False


class Storage:
    """Key/value data storage for modules."""
    def __init__(self, bot, mod):
        self.bot = bot
        self.default = {}
        self.storage = {}
        self.loaded = False
        self.mod = mod

    def __getitem__(self, attr):
        if attr in self.storage.keys():
            return self.storage[attr]
        return self.default[attr]
    
    def __setitem__(self, attr, val):
        self.storage[attr] = val

    def SetDefault(self, default):
        self.default = default
        if not self.loaded:
            self.storage = default
        return True

    def Store(self):
        if not self.mod.name in self.bot.config["modules"]:
            self.bot.config["modules"][self.mod.name] = {}
        self.bot.config["modules"][self.mod.name]["storage"] = self.storage
        res = self.bot.config.Store()
        return self.bot.config.Store()

    def Load(self):
        if self.mod.name in self.bot.config["modules"].keys():
            if "storage" in self.bot.config["modules"][self.mod.name].keys():
                self.storage = self.bot.config["modules"][self.mod.name]["storage"]
                self.loaded = True
        return self.loaded


class Module:
    """Base class for all modules."""
    def __init__(self, bot):
        self.bot = bot
        self.name = ""
        self.debug = 1
        self.last_exec = None
        self.storage = Storage(self.bot, self)

    def init(self):
        pass

    def Log(self, s, color=None):
        self.bot.log.Log("mod", "{"+self.name+"} "+s, color)

    def SetProperties(self, properties):
        for key in properties.keys():
            if key == "level":
                self.level = properties[key]
            if key == "zone":
                self.zone = properties[key]
            if key == "storage":
                self.storage.SetDefault(properties[key])
                self.storage.storage = properties[key]
        return True

    def GetMan(self):
        docstr = "-no description-"
        if "__doc__" in dir(self):
            docstr = " ".join(map(lambda s: s.strip(), self.__doc__.split("\n")))
        alias_str = ""
        aliases = self.bot.config.GetAliases(self.name)
        if aliases:
            alias_str = " (" + ", ".join(aliases) + ")"
        man = self.name + alias_str + " [" + str(self.level) + "]: " + docstr
        return man


class Command(Module):
    """Base class for commands."""
    def __init__(self, bot, properties):
        Module.__init__(self, bot)
        self.SetProperties(properties)
        self.name = properties["name"]

        self.args = Args()
        self.throttle_time = properties["throttle"]
        if self.throttle_time == None:
            self.throttle_time = self.bot.config["cmd_throttle"]

        self.initialized = 0
        self.users = {} # list of users of command
        
    def DebugCmd(self, *args):
        # FIXME: Deprecate this
        args = map(arg_to_str,args)
        line = " ".join(args)
        self.Log(line)
        
    def ArgList(self, data):
        if data == None: return []
        data = data.strip()
        argobj = Args(data.split(" "))
        return argobj
    
    def IsAllowedWin(self, win):
        if self.zone == IRC_ZONE_BOTH:
            return True
        else:
            if win.zone != self.zone:
                return False
        return True
        
    def IsAllowedUser(self, user):
        if user.GetPermission()<self.level:
            return False
        return True

    # Determine wether the command can be run
    # Blocks command spamming
    def IsThrottled(self,user):
        if user.GetPermission() >= 5:
            return False
        else:
            if user in self.users.keys():
                t = self.users[user][0]
                if (time.time()-t) < self.throttle_time:
                    return True
                else:
                    return False
            else:
                self.users[user] = [time.time(), False]
                return False

    def GetThrottleWaitTime(self,user):
        t = self.throttle_time - int(time.time() - self.users[user][0])
        if t < 1: t=1
        return t

    def WarnThrottle(self, user):
        if self.users[user][1] == False:
            self.users[user][1] = True
            return True
        else:
            return False

    def Execute(self, win, user, data, caller=None):
        if self.IsAllowedWin(win):
            if self.IsAllowedUser(user):
                if self.IsThrottled(user):
                    if self.WarnThrottle(user):
                        win.Privmsg("can't do that so often, wait %i sec" %self.GetThrottleWaitTime(user))
                    return False
                else:
                    self.users[user] = [time.time(), False]
                    if self.bot.config["avoid_cmd_crash"]:
                        try:
                            self.args = Args(data, self.bot)
                            self.run(win, user, data)
                        except Exception, e:
                            win.Privmsg("failed to run:" + str(e))
                            msg = get_error_info()
                            self.bot.log.Error("bot", msg)
                    else:
                        self.run(win, user, data)
                    return True
            else:
                if user.IsAuthed():
                    win.Privmsg("sry, you can't do that")
                else:
                    win.Privmsg("sry, you need to auth")
                
        else:
            win.Privmsg("you can't do that here, use privmsg")
        return False
    
    def run(self, win, user, data, caller=None):
        pass


class Listener(Module):
    """Base class for listeners."""
    def __init__(self, bot, properties):
        Module.__init__(self, bot)
        self.name = properties["name"]
        self.zone = properties["zone"]

        self.interval = properties["interval"]
        self.last_exec = None

        self.events = []

    def event(self, event):
        pass

    def ExecuteEvent(self, event):
        if self.bot.config["avoid_cmd_crash"]:
            try:
                self.last_exec = time.time()
                return self.event(event)
            except Exception, e:
                msg = get_error_info()
                self.bot.log.Error("bot", msg)
                return False
        else:
            self.last_exec = time.time()
            return self.event(event)


class Hybrid(Command, Listener):
    """Base class for hybrid modules, that are both commands and listeners."""
    def __init__(self, bot, properties):
        Command.__init__(self, bot, properties)
        Listener.__init__(self, bot, properties)
