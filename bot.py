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

import logger
import mods
import config

import comps
from comps import *

class IRCBot(irc.IRCClient):
    def __init__(self):
        self.log = logger.Logger(self)
        irc.IRCClient.__init__(self)
        self.commands = {}
        self.zones = [IRC_ZONE_QUERY, IRC_ZONE_CHANNEL, IRC_ZONE_BOTH]
        self.bot_running = 0
        self.bot_debugging = 1
        self.current_path = get_current_script_path()
        config_file = "config.txt"

        if len(sys.argv) > 1:
            config_file = sys.argv[1]
        if s60:
            self.config = config.BotConfig(self, "e:\\python\\config.txt")
        else:
            self.config = config.BotConfig(self, config_file)
        self.config.Load()
        
        # Setup the bot identity and command line user
        self.me = Me(self)
        self.admin = Admin(self)
        
        # Prepopulate users and windows
        self.users = [self.me, self.admin]
        self.windows = [Console(self, self.me)]

        self.commands = {}
        self.listeners = {}
        
        self.commands_cache = {}
        self.listeners_cache = {}
        
        self.LoadModules()
        self.log.Loaded()

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
        self.log.Log("bot", line)



    #
    #   Manage loading of bot config and modules
    #

    def ReloadBot(self):
        try:
            reload( comps )
            return True
        except Exception,e:
            msg = get_error_info()
            self.log.Error("bot", msg)
            return e
            
        self.me = None
        self.channels = []
        self.users = [self.me, self.admin]
        self.ReloadModules()
   
    def ReloadConfig(self):
        try:
            reload(config)
            self.config = config.BotConfig(self.config_file)
            self.config.Load()
        except Exception, e:
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
                self.RunListener(name)
            if mod["type"] == MOD_BOTH:
                self.listeners[name] = mod
                self.commands[name] = mod
                self.RunListener(name)
            
    def ReloadModules(self):
        try:
            import bot
            reload(__import__("mod_base"))
            reload(mods)
        except Exception,e:
            msg = get_error_info()
            self.log.Error("bot", msg)
            return e
        self.ResetModules()
        self.LoadModules()
        return True

    def EnableModule(self, name):
        if not name in mods.modules.keys():
            return False
        self.config.EnableMod(name)
        if name in self.listeners.keys():
            self.RunListener(name)

    def DisableModule(self, name):
        if not name in mods.modules.keys():
            return False
        self.config.DisableMod(name)
        if name in self.listeners_cache.keys():
            del self.listeners_cache[name]

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
        # Characters after cmd_prefix to ignore
        ignore = [" ", ".", "-", "!", "?", "_"]

        # Check if message begins with cmd_prefix
        if message[:len(self.config["cmd_prefix"])] == self.config["cmd_prefix"]:
            command = message[len(self.config["cmd_prefix"]):]
            if len(command) == 0:
                return False
            if command[0] in ignore:
                return False
            return command
        else: # If not, check if it begins with the bots nick
            parts = message.split(" ")
            if parts[0].lower().startswith(self.me.nick.lower()):
                rest =  parts[0].lower()[len(self.me.nick):]
                if not rest:
                    return "" # Return empty string to trigger unknown command event
                if rest[0] in [" ", ",", ";",":"]:
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

    def GetModule(self, name):
        mod = self.GetCommand(name)
        if mod:
            return mod

        if name in self.listeners.keys():
            return self.listeners_cache[name]
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
            args = ""
            if data:
                try:
                    args = unicode(data)
                except:
                    args = data
            data = data or None
            line = str(user)+" "+command+" "+args
            self.log.Log("bot", line, color=logger.colors.RED)
            inst.Execute(win, user, data)
        else:
            if not self.HandleEvent(Event(IRC_EVT_UNKNOWN_CMD, win, user, cmd = command, cmd_args=data)):
                win.Privmsg("don't understand")
    
    def RunListener(self, name):
        listener = self.listeners[name]
        instance = listener["class"](self, listener)
        if listener["type"] == MOD_BOTH:
            self.commands_cache[name] = instance
        self.listeners_cache[name] = instance
        return instance.init()

    def HandleEvent(self, event):
        handled = False
        for listener in self.listeners_cache.keys():
            # incase module removed during looping
            try:
                lstn = self.listeners_cache[listener]
            except:
                continue
            if IRC_EVT_ANY in lstn.events:
                lstn.ExecuteEvent(event)
            if event.id in lstn.events:
                value = lstn.ExecuteEvent(event)
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
            win = Query(self, self.GetUser(name, True))
            self.windows.append(win)
        return win
        
    def GetWindow(self, name, create=True):
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
        
    def GetUser(self, nick, create = False): # FIXME: default create to false
        for user in self.users:
            if user.nick == nick:
                return user
        if create:
            self.log.Info("bot", "Creating user "+nick)
            user = self.MakeUser(nick)
            return user
        return False

    def RemoveUser(self, nick):
        for user in self.users:
            if user.nick.lower() == nick.lower():
                self.users.pop(self.users.index(user))
                return True
        return False
        
    def FindUser(self, nick):
        for user in self.users:
            if user.nick.lower() == nick.lower():
                return user
        return False
        

    
        
    # Actions
        
    def DoAutoJoin(self):
        self.JoinChannels(self.config.GetAutoJoinChannels())
        
    def AuthenticateUser(self, user, name, pw):
        account = self.config.AuthenticateUser(name, pw)
        if account == False:
            return False
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
        
    def OnLoop(self):
        for listener in self.listeners_cache.keys():
            lstn = self.listeners_cache[listener]
            if IRC_EVT_INTERVAL in lstn.events:
                if not lstn.last_exec:
                    lstn.ExecuteEvent(Event(IRC_EVT_INTERVAL))
                elif time.time() - lstn.last_exec > lstn.interval:
                    lstn.ExecuteEvent(Event(IRC_EVT_INTERVAL))
             
    def OnInterrupt(self):
        print ""
        return self.HandleEvent(Event(IRC_EVT_INTERRUPT))

    def OnClientLog(self, line): # Route irc client class logging to BotLog
        self.log.Log("irc", line)
        # Returning True prevents the irc client class from printing the logging to the console
        return True
        
    def OnConnected(self):
        self.log.Log("bot", "Connected to IRC server.")
        self.DoIntroduce(self.me.nick, self.config["identity"]["ident"], self.config["identity"]["realname"])
        
    def OnReady(self):
        self.log.Log("bot", "IRC handshake done, now ready.")
        self.throttled = 0
        self.HandleEvent(Event(IRC_EVT_READY))
        self.DoAutoJoin()

    def OnNickInUse(self, nick, reason):
        self.me.TryNewNick()
        
    def OnUserHostname(self, nick, hostname):
        self.GetUser(nick, True).SetHostname(hostname)

    def OnWhoisHostname(self, nick, hostname):
        self.GetUser(nick, True).SetHostname(hostname)
        
    def OnUserNickChange(self, nick, new_nick):
        # Make sure nick doesn't exist, just in case.
        test_user = self.GetUser(new_nick)
        if test_user != False:
            # If it does exist, we remove the old user and show a warning.
            self.log.Warning("bot", nick+" changed to existing user: "+new_nick+". Something wrong!")
            self.RemoveUser(new_nick)
        self.GetUser(nick).OnNickChanged(nick, new_nick)
        
    def OnUserQuit(self, nick, reason):
        user = self.GetUser(nick)
        user.OnQuit(reason)
        for win in self.windows:
            if win.zone == IRC_ZONE_CHANNEL:
                if win.HasUser(user):
                    win.OnQuit(user, reason)
        
    def OnPrivmsg(self, by, to, msg):
        user = self.GetUser(by, True)
        if self.IsChannelName(to):
            win = self.GetWindow(to)
        else:
            win = self.GetWindow(by)
        win.OnPrivmsg(user,msg)
        self.HandleMessage(win, user, msg)

    def OnNotice(self, by, to, msg):
        user = self.GetUser(by, True)
        if self.IsChannelName(to):
            win = self.GetWindow(to)
        else:
            win = self.GetWindow(by)
        win.OnNotice(user,msg)
        
    def OnIJoined(self, chan):
        win = self.GetWindow(chan)
        win.OnIJoined()
        win.AddUser(self.me)

    def OnChannelHasUsers(self, chan, users):
        """ Called when the server indicates which users are present on a channel. """
        self.GetWindow(chan).OnHasUsers(users)
        
    def OnChannelModesChanged(self, chan, modes, nick):
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
        win.OnJoin(self.GetUser(nick, True))

    def OnChannelPart(self, chan, nick, reason):
        self.DebugLog("OnChannelPart(", chan, nick, reason, ")")
        self.GetWindow(chan).OnPart(self.GetUser(nick), reason)

    def OnChannelKick(self, chan, who, nick, reason):
        self.GetWindow(chan).OnKick(self.GetUser(who), self.GetUser(nick), reason)
        
    def OnChannelTopicIs(self, chan, topic):
        self.GetWindow(chan).OnTopicIs(topic)
        
    def OnChannelTopicMeta(self, chan, nick, utime):
        self.GetWindow(chan).OnTopicMeta(nick, utime)
        
    def OnChannelTopicChanged(self, chan, by, topic):
        user = self.GetUser(by)
        self.GetWindow(chan).OnTopicChanged(topic, user)
        
    def RunBot(self):
        self.bot_running = 1

        self.log.Log("bot", "Starting bot...")
        self.SetHost(self.config["server"]["host"])
        self.SetPort(self.config["server"]["port"])
        self.SetSendThrottling(self.config["send_throttle"])
        
        status = self.BotLoop()
        self.log.Log("bot", "Run()","bot loop returned status", status)
        self.log.Log("bot", "Run()","terminated!")
        return status

    def StopBot(self):
        self.irc_running = 0
        self.bot_running = 0
        return True
        
    def BotLoop(self):
        self.StartClient()
        while self.bot_running:
            self.log.Log("bot", "BotLoop()","client disconnected")
            if self.irc_throttled:
                time.sleep(self.config["throttle_wait"])
            else:
                self.log.Log("bot", "BotLoop()","reconnecting in 10sec")
                time.sleep(10)
            self.StartClient()
            self.log.Log("bot", "BotLoop()","client disconnected")

if __name__ == "__main__":
    b = IRCBot()
    b.RunBot()
