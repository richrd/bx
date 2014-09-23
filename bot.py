# -*- coding: utf-8 -*-
"""
Cross platform IRC Bot.

Tested on linux and Nokia Symbian S60v3.

Features
- Extendable with reloadable easy to write commands and events
- Provides windows, events and commands with user management and authentication
"""

import os
import sys
import time
import string
import traceback

# Symbian S60 specific compatibility
s60 = False
if sys.platform == "symbian_s60":
    s60 = True
    sys.path.append("e:\\python")
    sys.path.append("c:\\python")
    sys.path.append("c:\\DATA\\python")

import irc
from helpers import *
from const import *

import mods
import config

import comps
from comps import *


class IRCBot(irc.IRCClient):
    def __init__(self):
        irc.IRCClient.__init__(self)
        self.commands = {}
        self.zones = [IRC_ZONE_QUERY, IRC_ZONE_CHANNEL, IRC_ZONE_BOTH]
        self.bot_running = 0
        self.bot_debugging = 1
        self.current_path = get_current_script_path()
        
        conf_file = "config.txt"

        if len(sys.argv) > 1:
            conf_file = sys.argv[1]
        if s60:
            self.config = config.BotConfig("e:\\python\\config.txt")
        else:
            self.config = config.BotConfig(conf_file)
        self.config.Load()
        
        self.me = Me(self)
        
        self.users = [self.me]
        self.windows = []
                
        self.commands = {}
        self.listeners = {}
        
        self.commands_cache = {}
        self.listeners_cache = {}
        
        self.LoadModules()

    #
    # Logging
    #
        
    def BotLog(self, *args):
        try:
            x = self.bot_running
        except:
            return False
        args = map(arg_to_str, args)
        line = " ".join(args)
        if self.bot_debugging:
            print time_stamp_short(),"BOT :: ",(line)



    #
    #   Manage loading of bot config and modules
    #

    def ReloadBot(self):
        try:
            reload( comps )
            from comps import *
            return True
        except Exception,e:
            print traceback.format_exc()
            print sys.exc_info()[0]
            return e
            
        self.me = None
        self.channels = []
        self.users = []
        self.ReloadModules()
   
    def ReloadConfig(self):
        try:
            reload(config)
            self.config = config.BotConfig("config.txt")
            self.config.Load()
        except Exception,e:
            return e
        return True
        
    def ResetModules(self):
        self.commands = {}
        self.listeners = {}
        
        self.commands_cache = {}
        self.listeners_cache = {}
        
    def LoadModules(self):
        use = self.config.GetMods()
        self.commands = {}
        self.listeners = {}
        modules = mods.modules

        for name in modules.keys():
            if not name in use:
                continue
            mod = modules[name]
            mod = self.config.ApplyModConfig(mod)
            if mod["type"] == MOD_COMMAND:
                self.commands[name] = mod
            if mod["type"] == MOD_LISTENER:
                self.listeners[name] = mod
            if mod["type"] == MOD_BOTH:
                self.commands[name] = mod
                self.listeners[name] = mod
                self.RunListener(name)
            
    def ReloadModules(self):
        try:
            import bot
            reload(mods)
        except Exception,e:
            print traceback.format_exc()
            print sys.exc_info()[0]
            return e
        self.ResetModules()
        self.LoadModules()
        return True


    #
    #   Run commands and events
    #
        
    def HandleMessage(self, win, user, msg):
        self.HandleEvent(Event(IRC_EVT_MSG, win, user, msg))
        command = self.FindCommand(msg)
        if command != False:
            data = None
            if command.find(" ") != -1:
                data = command[command.find(" ") + 1:]
                command = command[:command.find(" ")].lower()
            else:
                command = command.lower()
            if data == "": data = None
            self.RunCommand(command, win, user, data)
            
    def FindCommand(self, message):
        if message[:len(self.config["cmd_prefix"])] == self.config["cmd_prefix"]:
            command = message[len(self.config["cmd_prefix"]):]
            if len(command) == 0:
                return False
            if command[0] in [" ", ".", "-", "!", "?", "_"]:
                return False
            return command
        else:
            parts = message.split(" ")
            if parts[0].lower().startswith(self.me.nick.lower()):
                return " ".join(parts[1:])
        return False

    def GetCommand(self, name):
        alias = self.config.AliasToCommand(name)
        if alias:
            name = alias
        if name in self.commands_cache.keys():
            return self.commands_cache[name]
        if name in self.commands.keys():
            command = self.commands[name]
            instance = command["class"](self, command)
            self.commands_cache[name] = instance
            instance.init()
            return instance
        return False
        
    def GetCommandsByPermission(self, level = 0):
        cmds = []
        for command in self.commands.keys():
            cmd_level = self.commands[command]["level"]
            if cmd_level > level: continue
            cmds.append(command)
        return cmds
        
    def RunCommand(self, command, win, user, data):
        inst = self.GetCommand(command)
        if inst != False:
            self.BotLog("RunCommand(", command, user, data, ")")
            inst.Execute(win, user, data)
        else:
            if not self.HandleEvent(Event(IRC_EVT_UNKNOWN_CMD, win, user, cmd = command, cmd_args=data)):
                win.Privmsg("don't understand")
    
    def RunListener(self, name):
        listener = self.listeners[name]
        instance = listener["class"](self, listener)
        self.listeners_cache[name] = instance
        instance.init()

    def HandleEvent(self, event):
        handled = False
        for listener in self.listeners_cache.keys():
            lstn = self.listeners_cache[listener]
            if IRC_EVT_ANY in lstn.events:
                lstn.event(event)
            if event.id in lstn.events:
                value = lstn.event(event)
                if not handled:
                    handled = value or False
        return handled



    #
    #   Manage virtual windows
    #
    
    def MakeWindow(self, name):  #When we make a window, we need to set it up with stuff from the config file
        if self.IsChannelName(name):
            win = Channel(self, name)
            self.windows.append(win)
        else:
            win = Query(self, self.GetUser(name))
            self.windows.append(win)
        return win
        
    def GetWindow(self, name, create=True): # FIXME: default create to False
        for win in self.windows:
            if win.GetName() == name:
                return win
        if create:
            win = self.MakeWindow(name)
            return win
        else:
            return False
        
    def MakeUser(self, nick):
        user = User(self, nick)
        self.users.append(user)
        return user
        
    def GetUser(self, nick, create = True):
        for user in self.users:
            if user.nick == nick:
                return user
        if create:
            user = self.MakeUser(nick)
            return user
        return False
        
    def FindUser(self, nick):
        for user in self.users:
            if user.nick.lower() == nick.lower():
                return user
        return False
        

    
        
    # Actions
        
    def DoAutoJoin(self):
        self.BotLog("DoAutoJoin()")
        self.JoinChannels(self.config.GetAutoJoinChannels())
        
    def AuthenticateUser(self, user, name, pw):
        account = self.config.AuthenticateUser(name,pw)
        if account == False:return False
        user.OnAuthed(account)
        return True
            
    def AuthenticateHostname(self, user, hostname):
        account = self.config.AuthenticateHostname(hostname)
        if account == False:
            return False
        user.OnAuthed(account)
        return True
        
        
        
    #
    #   Events
    #
        
    def OnClientLog(self, line): # Route irc client class logging to BotLog
        pass
        # self.BotLog(line)
        # Returning True prevents the irc client class from printing the logging to the console
        # return True
        
    def OnConnected(self):
        self.DebugLog("OnConnected()")
        self.DoIntroduce(self.me.nick,self.config["ident"],self.config["realname"])
        
    def OnNickInUse(self, nick, reason):
        self.BotLog("OnNickInUse(", nick, reason, ")")
        self.me.TryNewNick()
        
    def OnUserHostname(self, nick, hostname):
        #self.BotLog("OnUserHostname(",nick,",",hostname,")")
        self.GetUser(nick).SetHostname(hostname)
        pass

    def OnWhoisHostname(self, nick, hostname):
        #self.BotLog("OnWhoisHostname(",nick,",",hostname,")")
        self.GetUser(nick).SetHostname(hostname)
        pass
        
    def OnUserNickChange(self, nick, new_nick):
        #self.BotLog("OnUserNickChange(",nick,new_nick,")")
        self.GetUser(nick).OnNickChanged(nick,new_nick)
        
    def OnUserQuit(self, nick, reason):
        self.BotLog("OnUserQuit(",nick,reason,")")
        user = self.GetUser(nick)
        user.OnQuit(reason)
        for win in self.windows:
            if win.zone == IRC_ZONE_CHANNEL:
                if win.HasUser(user):
                    win.OnQuit(user,reason)
                

        
        
    def OnReady(self):
        self.BotLog("OnReady()")
        self.throttled = 0
        self.HandleEvent(Event(IRC_EVT_READY))
        self.DoAutoJoin()
        
    def OnPrivmsg(self, by, to, msg):
        user = self.GetUser(by)
        if self.IsChannelName(to):
            win = self.GetWindow(to)
        else:
            win = self.GetWindow(by)
        win.OnPrivmsg(user,msg)
        self.HandleMessage(win, user, msg)

    def OnNotice(self, by, to, msg):
        user = self.GetUser(by)
        if self.IsChannelName(to):
            win = self.GetWindow(to)
        else:
            win = self.GetWindow(by)
        win.OnNotice(user,msg)
        
    def OnIJoined(self, chan):
        self.BotLog("JOINED", chan)
        win = self.GetWindow(chan)
        win.OnIJoined()
        win.AddUser(self.me)

        
        
    def OnChannelHasUsers(self, chan, users):
        """ Called when the server indicates which users are present on a channel. """
        #self.DebugLog("OnChannelHasUsders(",chan,",",users,")")
        self.GetWindow(chan).OnHasUsers(users)
        
    def OnChannelModesChanged(self, chan, modes, nick):
        self.DebugLog("OnChannelModesChanged(", chan, modes, ")")
        user = self.GetUser(nick)
        win = self.GetWindow(chan)
        win.OnModesChanged(modes, user)

    def OnChannelUserModesChanged(self, chan, nickmodes, by):
        usermodes = []
        for nickm in nickmodes:
            usermodes.append( (self.GetUser(nickm[0]),nickm[1],nickm[2]) )
        self.GetWindow(chan).OnUserModesChanged(usermodes,by)
        
    def OnChannelJoin(self, chan, nick):
        win = self.GetWindow(chan)
        win.OnJoin(self.GetUser(nick))
        #self.DebugLog("OnChannelJoin(",chan,nick,")")

    def OnChannelPart(self, chan, nick, reason):
        self.DebugLog("OnChannelPart(", chan, nick, reason, ")")
        self.GetWindow(chan).OnPart(self.GetUser(nick), reason)

    def OnChannelKick(self, chan, who, nick, reason):
        self.GetWindow(chan).OnKick(self.GetUser(who), self.GetUser(nick), reason)
        
    def OnChannelTopicIs(self, chan, topic):
        #self.DebugLog("OnChannelTopicIs(",chan,",",topic,")")
        self.GetWindow(chan).OnTopicIs(topic)
        
    def OnChannelTopicMeta(self, chan, nick, utime):
        #self.DebugLog("OnChannelTopicMeta(",chan,",",nick,",",utime,")")
        self.GetWindow(chan).OnTopicMeta(nick, utime)
        
    def OnChannelTopicChanged(self, chan, by, topic):
        #self.DebugLog("OnChannelTopicChanged(",chan,",",topic,",",by,")")
        user = self.GetUser(by)
        self.GetWindow(chan).OnTopicChanged(topic, user)
        
    def RunBot(self):
        self.BotLog("Run()")
        self.bot_running = 1

        self.BotLog("Run()","starting bot...")
        self.SetHost(self.config["host"])
        self.SetPort(self.config["port"])
        self.SetSendThrottling(self.config["send_throttle"])
        
        status = self.BotLoop()
        self.BotLog("Run()","bot loop returned status",status)
        self.BotLog("Run()","terminated!")
        return status

    def StopBot(self):
        self.irc_running = 0
        self.bot_running = 0
        return True
        
    def BotLoop(self):
        self.BotLog("BotLoop()")
        self.StartClient()
        while self.bot_running:
            self.BotLog("BotLoop()","client disconnected")
            if self.irc_throttled:
                time.sleep(self.config["throttle_wait"])
            else:
                self.BotLog("BotLoop()","reconnecting in 10sec")
                time.sleep(10)
            self.StartClient()
            self.BotLog("BotLoop","client disconnected")

if __name__ == "__main__":
    b = IRCBot()
    b.RunBot()
