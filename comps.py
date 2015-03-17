# -*- coding: utf-8 -*-
"""
Bot Components

Provides virtual windows, users, events etc. for the bot.

"""

import os
import sys
import time
import string
# import traceback

# Symbian S60 specific compatibility
s60 = False
if sys.platform == "symbian_s60":
    s60 = True
    sys.path.append("e:\\python")
    sys.path.append("c:\\python")
    sys.path.append("c:\\DATA\\python")

from helpers import *
from const import *


class Event:
    """Event object

    Stores events to facilitate passing events around easily

    """
    # TODO: make this more manageable
    def __init__(self, id, win=None, user=None, msg=None, modes=None, mode_oper=None, cmd=None, cmd_args=None, by=None, new_nick=None):
        self.time = time.time()
        self.id = id #FIXME: rename to 'type'
        self.type = id
        self.win = win
        self.user = user
        self.msg = msg

        self.modes = modes
        self.mode_oper = mode_oper

        self.cmd = cmd
        self.cmd_args = cmd_args
        self.by = by
        self.new_nick = new_nick

    def __str__(self):
        s = "Event("
        s += "," + str(self.id)
        s += "," + str(self.win)
        s += "," + str(self.user)
        s += "," + safe_escape(self.msg)

        s += "," + str(self.modes)
        s += "," + str(self.mode_oper)

        s += "," + str(self.cmd)
        s += "," + str(self.cmd_args)
        s += ")"
        return s


class Message:
    """Message object

    Stores an irc message and its details.

    """
    def __init__(self,nick,text,dest=""):
        self.time = time.time()
        self.nick = nick
        self.text = text
        self.dest = dest

    def __str__(self):
        return "["+time_stamp(self.time)+"] "+self.nick+" -> "+self.dest+" :"+self.text




#
# Users
#
class User:
    """User object

    Represents each user the bot is aware of.

    """
    def __init__(self, bot, nick=""):
        self.bot = bot
        self.nick = u""+nick
        self.hostname = u""
        self.ident = u""

        self.debug = 1
        
        self.online = 1
        self.created = time.time()
        
        self.went_online = None
        self.went_offline = None
        self.quit_reason = None
        
        self.last_active = None
        self.last_command = None

        self.account = False     # If False the user hasn't logged in

    def __repr__(self):
        return "<" + self.nick + ">"
        
    def __str__(self):
        return "<" + self.nick + ">"
        
    def InfoStr(self):
        s = "<" + self.nick + "> "
        s += " hn:" + self.hostname
        s += " crtd:" + time_stamp_numeric(self.created)
        s += " online:" + str(self.online)
        if self.last_active:
            s += " act:" + time_stamp_numeric(self.last_active)
        if self.went_offline:
            s += " quit:" + time_stamp_numeric(self.went_offline)
        if self.account:
            s += " id:" + self.account["name"]
        return s
        
    def DebugLog(self, *args):
        args = map(arg_to_str, args)
        line = self.__str__() + " " + " ".join(args)
        if self.debug:
            self.bot.log.Log("user", line)

    #
    #   Events
    #
            
    def OnAction(self):
        self.online = 1
        self.last_active = time.time()
        pass
        
    def OnOnline(self): #FIXME implement
        self.AutoAuth()
        self.OnAction()
    
    def OnNickChanged(self, old, new):
        self.bot.HandleEvent(Event(IRC_EVT_USER_NICK_CHANGE, user=self, new_nick=new))
        self.OnAction()
        self.DebugLog("changed nick from", old, "to", new)
        self.nick = u"" + new
        
    def OnHostnameChanged(self, old, new):
        self.OnAction()
        self.DebugLog("HOST ", new)
        self.hostname = new
        if self.AutoAuth():
            return True
        self.Deauth()
        return True
        
    def OnQuit(self, reason):
        self.DebugLog("OnQuit(", reason, ")")
        if reason:
            self.quit_reason = reason
        self.went_offline = time.time()
        self.online = 0
        self.Deauth()
        
    def OnAuthed(self, account):
        self.OnAction()
        self.account = account
        self.bot.HandleEvent(Event(IRC_EVT_USER_AUTHED, user = self))
        
        
    #
    # Actions
    #
    
    def Privmsg(self, msg):
        self.bot.Privmsg(self.GetNick(), msg)
        
    def Notice(self, msg):
        self.bot.Notice(self.GetNick(), msg)
        
    def Send(self, msg):
        send = "privmsg"
        if self.bot.config["default_send"] == "notice":
            send = "notice"
        if send == "notice":
            self.bot.Notice(self.GetNick(), msg)
        else:
            self.bot.Privmsg(self.GetNick(), msg)
        
        
    #
    # Internal stuff
    #
            
    def AutoAuth(self):
        if not self.IsAuthed():
            if self.bot.AuthenticateHostname(self, self.hostname):
                return True
            return False
        return False

    def Deauth(self):
        if self.IsAuthed():
            self.account = False
            return True
        else:
            return False

    def IsAuthed(self):
        if self.account == False:
            return False
        return True

    def IsOnline(self):
        if self.online:
            return True
        return False

    #
    # Getters
    #
        
    def GetNick(self):
        return self.nick

    def GetQuery(self):
        return self.bot.GetWindow(self.GetNick())

    def GetPermission(self):
        if self.account == False:
            return 0
        else:
            return self.account["level"]

    def Channels(self):
        chans = []
        for win in self.bot.windows:
            if win.zone == IRC_ZONE_CHANNEL:
                if win.HasUser(self):
                    chans.append(win)
        return chans
            
    def HasOP(self, chan):
        return chan.UserHasMode(self, IRC_MODE_OP)

    def HasVoice(self, chan):
        return chan.UserHasMode(self, IRC_MODE_VOICE)

    def SetHostname(self, hostname):
        if hostname != self.hostname:
            self.OnHostnameChanged(self.hostname, hostname)
            return True
        if not self.IsOnline():
            self.OnOnline()
        return False


class Me(User):
    """Me object

    Represents the bot as an irc user and does nick management for the bot.

    """
    def __init__(self, bot):
        User.__init__(self, bot, bot.config["identity"]["nicks"][0])
        self.nick_index = 0
        self.attempted_nick = self.nick
        self.bot.SetNick(self.nick)
        
    def Nick(self, nick=None):
        if nick == None:
            nick = self.nick
        else:
            self.nick = nick
        self.attempted_nick = nick
        self.bot.ChangeNick(nick)
        
    def TryNewNick(self):
        self.DebugLog("TryNewNick()")
        self.attempted_nick = self.attempted_nick + self.bot.config["identity"]["nick_suffix"]
        # The attempted nick might not be available but we
        # store it as the current nick assuming it will succeed
        # (it eventually will anyway and then nick will be correct)
        # This is the easiest way to maintain the correct nick
        self.nick = self.attempted_nick
        self.bot.ChangeNick(self.attempted_nick)

class Admin(User):
    """Admin user

    Represents the command line user.

    """
    def __init__(self, bot):
        User.__init__(self, bot, "*admin*")
        self.account = {"level": 100}

    def Privmsg(self, msg):
        self.Send(msg)

    def Notice(self, msg):
        self.Send(msg)

    def Send(self, msg):
        self.bot.log.Info("bot", msg)

#
# Virtual windows
#

class BotWindow:
    """Window representing an IRC channel or query"""

    def __init__(self, bot, name=None):
        self.bot = bot
        self.name = name
        self.zone = None
        self.log = []
        self.debug = 1

    def __repr__(self):
        return "[" + self.GetName() + "]"

    def __str__(self):
        return "[" + self.GetName() + "]"
        
    def DebugLog(self, *args):
        args = map(arg_to_str, args)
        line = self.__str__() + " " + " ".join(args)
        if self.debug:
            self.bot.log.Log("win", line)
        
    def GetName(self):
        return self.name
        
    def GetNicks(self):
        return []
        
    def FlushLogs(self):
        while len(self.log) >= self.bot.config["default_log_limit"]:
            self.log.pop(0)
        
    def AppendLog(self, msg):
        self.FlushLogs()
        self.log.append(msg)
        
    def Privmsg(self, msg):
        self.bot.Privmsg(self.GetName(), msg)

    def Notice(self, msg):
        self.bot.Notice(self.GetName(), msg)
        
    def Send(self, msg):
        send = "privmsg"
        if self.bot.config["default_send"] == "notice":
            send = "notice"
        if send == "notice":
            self.bot.Notice(self.GetName(), msg)
        else:
            self.bot.Privmsg(self.GetName(), msg)
            
    def OnPrivmsg(self, user, msg):
         message = Message(user.GetNick(), msg, self.GetName())
         self.AppendLog(message)

    def OnNotice(self, user, msg):
         self.DebugLog("*NOTICE*", user, msg)

        
class Query(BotWindow):
    def __init__(self, bot, user):
        BotWindow.__init__(self, bot)
        self.zone = IRC_ZONE_QUERY
        self.user = user

    def GetName(self):
        return self.user.nick

    def GetNicks(self):
        return [self.user.nick]

class Console(BotWindow):
    def __init__(self, bot, user):
        BotWindow.__init__(self, bot)
        self.zone = IRC_ZONE_QUERY
        self.user = user

    def GetName(self):
        return self.user.nick

    def GetNicks(self):
        return [self.user.nick]
        
    def Privmsg(self, msg):
        self.Send(msg)

    def Notice(self, msg):
        self.Send(msg)

    def Send(self, msg):
        self.bot.log.Info("bot", msg)
        
class Channel(BotWindow):
    def __init__(self, bot, name):
        BotWindow.__init__(self, bot, name)
        self.zone = IRC_ZONE_CHANNEL

        self.modes = []
        self.created = None
        self.topic = ""
        self.topic_by = None
        self.topic_time = None
        
        #List of users and their settings (modes etc)
        self.users = {}

    def GetNicks(self):
        nicks = []
        for user in self.users.keys():
            nick = user.GetNick()
            if not nick in self.bot.config["ignore_nicks"]:
                nicks.append(nick)
        return nicks
        
    def GetUsers(self):
        users = []
        for user in self.users.keys():
            nick = user.GetNick()
            if not nick in self.bot.config["ignore_nicks"]:
                users.append(user)
        return users
        
    def HasUser(self, user):
        return user in self.users.keys()

    def HasNick(self, nick):
        for user in self.users.keys():
            if user.GetNick().lower() == nick.lower():
                return True
        return False
        
    def AddUser(self, user, mode=None):
        if not self.HasUser(user):
            self.users[user] = {"modes":[]}
            if mode != None:
                self.OnUserHasMode(user, mode)
        else:
            if mode == None:
                self.users[user]["modes"] = []      #  Reset modes
            else:
                self.OnUserHasMode(user, mode)
        return user
        
    def RemoveUser(self, user):
        if user in self.users.keys():
            del self.users[user]

    def OnModesChanged(self, modes, user):
        self.bot.HandleEvent(Event(IRC_EVT_CHAN_MODE_CHANGE, self, user, modes=modes))

    def OnUserHasMode(self, user, mode):
        self.users[user]["modes"] = [mode]
            
    def OnUserModesChanged(self, usermodes, by):
        self.DebugLog("*MODES*", usermodes, "(", by, ")")
        for um in usermodes:
            self.UserModeChange(um[0], um[1], um[2])

    def UserModeAdd(self, user, mode):
        self.DebugLog("UserModeAdd", user, mode)
        mode = u"" + mode
        if not self.UserHasMode(user, mode):
            if not mode in self.users[user]["modes"]:
                self.users[user]["modes"].append(mode)
                return True
            return False
        return False
            
    def UserModeRemove(self, user, mode):
        self.DebugLog("UserModeRemove", user, mode)
        mode = u"" + mode
        if self.UserHasMode(user, mode):
            if mode in self.users[user]["modes"]:
                self.users[user]["modes"].pop(self.users[user]["modes"].index(mode))
                return True
            return False
        return False

    def UserModeChange(self, user, mode, oper):
        if not self.HasUser(user):
            return False
        if oper:
            status = self.UserModeAdd(user, mode)
        else:
            status = self.UserModeRemove(user, mode)
        self.bot.HandleEvent(Event(IRC_EVT_CHAN_USER_MODE_CHANGE, self, user, modes=mode, mode_oper=oper))
        return status

    def OnIJoined(self):
        self.DebugLog("*JOINED*")
        self.users = {}
        self.bot.HandleEvent(Event(IRC_EVT_I_JOINED, self, self.bot.me))

    def OnJoin(self, user):
        self.DebugLog("*JOIN* ", user)
        self.AddUser(user)
        user.OnAction()
        self.bot.HandleEvent(Event(IRC_EVT_CHAN_JOIN, self, user))

    def OnPart(self, user, reason):
        self.DebugLog("*PART*", user, "(", reason, ")")
        self.RemoveUser(user)
        user.OnAction()
        self.bot.HandleEvent(Event(IRC_EVT_CHAN_PART, self, user))

    def OnKick(self, user, by, reason):
        self.DebugLog("*KICK*", user, "by", by, "(", reason, ")")
        self.RemoveUser(user)
        user.OnAction()
        self.bot.HandleEvent(Event(IRC_EVT_CHAN_KICK, self, user, by=by, msg=reason))

    def OnQuit(self, user, reason):
        self.RemoveUser(user)
        
    def OnTopicIs(self, topic):
        self.DebugLog("*TOPIC* ", topic)
        self.topic = u"" + topic
        self.bot.HandleEvent(Event(IRC_EVT_CHAN_TOPIC, self))

    def OnTopicMeta(self, by, t):
        self.DebugLog("*TOPIC* by", by, "at", t)
        self.topic_by = by
        self.topic_time = t
        
    def OnTopicChanged(self, topic, user):
        nick = user.GetNick()
        self.DebugLog("*TOPIC*", topic, "[by ", nick, "]")
        self.topic = topic
        self.topic_by = nick
        self.topic_time = time.time()
        user.OnAction()

    def OnHasUsers(self, users):
        modes = {None:"","o":"@","v":"+"}
        nicks = ", ".join([modes[item[1]]+item[0] for item in users])
        self.DebugLog("*USERS*", nicks)
        for u in users:
            nick = u[0]
            mode = u[1]
            user = self.bot.GetUser(nick, True)
            self.AddUser(user, mode)

    #
    # Actions
    #

    def SetModes(self, modes):
        self.bot.SetChannelModes(self.GetName(), modes)

    def SetUserModes(self, usermodes, operation=True):
        nickmodes = []
        for item in usermodes:
            if operation:
                if self.UserHasMode(item[0], item[1]):
                    continue
            else:
                if not self.UserHasMode(item[0], item[1]):
                    continue
            nickmodes.append( (item[0].GetNick(), item[1]) )
        if nickmodes == []:
            return False
        self.bot.SetChannelUserModes(self.GetName(), nickmodes, operation)
        
    def GiveUserModes(self, users, mode):
        usermodes = []
        for user in users:
            usermodes.append((user, mode))
        self.SetUserModes(usermodes, True)
        
    def TakeUserModes(self, users, mode):
        usermodes = []
        for user in users:
            usermodes.append((user, mode))
        self.SetUserModes(usermodes, mode, False)
        
    def UserHasMode(self, user, mode):
        if user in self.users:
            return mode in self.users[user]["modes"]
        return False
        
    def SetTopic(self, topic):
        self.bot.SetChannelTopic(self.GetName(), topic)

    def Kick(self, user, reason=""):
        self.bot.Kick(self.GetName(), user.GetNick(), reason)
