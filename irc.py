# -*- coding: utf-8 -*-
"""irc.py: IRC Client Implementation

Handles all neccessary parts of the IRC protocol for client connections.

"""

import os
import sys
import time
import string
import select
import socket

# Symbian S60 specific compatibility
s60 = False
if sys.platform == "symbian_s60":
    s60 = True
    sys.path.append("e:\\python")
    sys.path.append("c:\\python")
    sys.path.append("c:\\DATA\\python")

from const import *
from helpers import *


class IRCClient:
    def __init__(self, host="", port=6667):
        """Independet irc client that will connect and sit in irc doing nothing.
        It can be subclassed to do whatever, with no need to worry about the protocol.
        """

        # Server details
        self.host = host
        self.port = port

        # User info defaults
        self.def_nick = "bx"
        self.def_realname = "bx"
        self.def_ident = "bx"

        # User info
        self.realname = None
        self.ident = None
        
        self.irc_debugging = True # wether to show debug output 

        # flag indicating wether the server throttled a connection attempt
        self.irc_throttled = 0

        # wait 8 minutes if server is throttling connects
        self.throttle_wait = 8*60

        # minimum time in seconds between sending lines to server
        self.send_throttling = 1
        
        # encoding to use when sending data
        self.encoding = "utf-8"

        # encodings used to try to decode incomming data
        self.decodings = ["utf-8", "latin-1", "cp1251", "cp1252", "win1251", "iso-8859-1"] 

        # FIXME tweak code to allways send at most 512 characters
        self.max_line_len = 400     # Maximum amount of characters sent to the server at once
        
        self.InitializeClient()

    def InitializeClient(self):
        """Reset variables before connecting."""
        self.DebugLog("Initializing...")
        self.nick = None

        self.irc_connected = False
        self.irc_running = False
        self.irc_ready = False
        #self.irc_throttled = 0
        
        self.sock = None
        self.sock_timeout = 20 # 20 sec timeout for socket
        self.select_timeout = .02

        # Time of last successfull connection
        self.connection_time = None
        

        # Received data:
        # Received and decoded data is appended to raw_buffer.
        # It is split into lines which are appended to recv_buffer.
        # Lines in recv_buffer are processed and removed from the buffer periodically.
        self.read_chunk_size = 1024
        self.raw_buffer = ""
        self.recv_buffer = []
        self.last_receive = None

        self.last_ping_pong = None # Timestamp of the last ping from server
        self.pinged_server = False
        self.ping_after = 120   # Seconds of inactivity after which the server is pinged
        self.max_inactivity = 180   # Total time to wait before reconnecting

        self.send_buffer = []           # lines queued to be sent
        self.send_time = None           # time of previous send

    def DebugLog(self, *args):
        args = map(arg_to_str, args)
        line = " ".join(args)
        self.PrintToLog(line)

    # Move this to DebugLog
    def PrintToLog(self, line):
        if not self.irc_debugging:
            return False
        log = line
        if not self.OnClientLog(log):
            print log

    def SetDebugging(self, b):
        self.irc_debugging = b
        
    def SetHost(self, host):
        self.host = host
        
    def SetPort(self, port):
        self.port = port
        
    def SetNick(self, nick): # Used to make sure current_nick is up to date
        self.nick = nick
        self.current_nick = nick

    def SetSendThrottling(self, seconds):        # Set minimum time to wait between sending lines to the server
        self.send_throttling = seconds
        
    def SetEncoding(self, enc):          # Set encoding to use when sending data
        self.encoding = enc
        
    def SetDecodings(self, decodings):   # Set list of encodings used to try to decode incomming data
        self.decodings = decodings

    #
    # Events
    #
    
    def OnClientLog(self, line):       # Used to intercept logs if returns True
        return False
    
    def OnConnectThrottled(self, reason=""):
        """Called when the server refuses to connect for some reason."""
        self.DebugLog("OnConnectThrottled(", reason, ")")
        self.irc_throttled = 1
    
    def OnConnected(self):
        self.irc_running = 1
        self.DoIntroduce(self.nick)
    
    def OnDisconnected(self):
        pass
        
    def OnLoop(self):
        """Run each time the bot loop is run. Only used if overriden."""
        pass
        
    def OnReceive(self, data):
        """Called when data is received from the server."""
        pass
        
    def OnNickInUse(self, nick, reason):
        self.DebugLog("OnNickInUse(", nick, reason, ")")
        self.nick = self.nick + "_"
        self.current_nick = self.nick
        self.ChangeNick(self.nick)
        
    def OnPing(self, data=False):
        data = data or ""
        self.last_ping_pong = time.time()
        self.SendLine("PONG %s" % data)
        
    def OnPong(self, data=False):
        self.last_ping_pong = time.time()
        
    def OnWelcomeInfo(self, info):
        #self.DebugLog("OnWelcomeInfo(", info, ")")
        pass

    def OnSupportInfo(self, info):
        #self.DebugLog("OnSupportInfo(", info, ")")
        pass

    def OnServerInfo(self, info):
        #self.DebugLog("OnServerInfo(", info, ")")
        pass

    def OnProcessConn(self, message):
        self.DebugLog("Waiting: ", message)

    def OnYourId(self, id, message = ""):
        pass

    def OnMotdLine(self, line):
        pass
        
    def OnReady(self):
        self.DebugLog("OnReady()")
        self.irc_throttled = 0
        
    def OnUserHostname(self, nick, hostname):
        pass

    def OnWhoisHostname(self, nick, hostname):
        #self.DebugLog("OnWhoisHostname(", nick, ",", hostname, ")")
        pass
        
    def OnUserNickChange(self, nick, new_nick):
        #self.DebugLog("OnUserNickChange(", nick, new_nick, ")")
        pass
        
    def OnUserQuit(self, nick, reason):
        self.DebugLog("OnUserQuit(", nick, reason, ")")

    def OnPrivmsg(self, by, to, msg):
        self.DebugLog("OnPrivmsg(", by, "->", to, "::", msg, ")")

    def OnNotice(self, by, to, msg):
        self.DebugLog("OnNotice(", by, "->", to, "::", msg, ")")

    def OnMyModesChanged(self, modes):
        self.DebugLog("OnMyModesChanged(", modes, ")")
        
    def OnIJoined(self, chan):
        self.DebugLog("OnIJoined(", chan, ")")

    def OnChannelInviteOnly(self, chan, reason):
        """ Called when the server indicates which users are present on a channel. """
        self.DebugLog("OnChannelInviteOnly(", chan, ",", reason, ")")
    
    def OnChannelNeedsPassword(chan, reason):
        self.DebugLog("OnChannelNeedsPassword(", chan, ",", reason, ")")
        
    def OnChannelHasUsers(self, chan, users):
        """ Called when the server indicates which users are present on a channel. """
        self.DebugLog("OnChannelHasUsers(", chan, ",", users, ")")
        
    def OnChannelJoin(self, chan, nick):
        self.DebugLog("OnChannelJoin(", chan, nick, ")")

    def OnChannelPart(self, chan, nick, reason):
        self.DebugLog("OnChannelPart(", chan, nick, reason, ")")
        
    def OnChannelKick(self, chan, who, nick, reason):
        self.DebugLog("OnChannelKick(", chan, ",", who, nick, reason, ")")
        
    def OnChannelCreated(self, chan, value):
        self.DebugLog("OnChannelCreated(", chan, value, ")")
    
    def OnChannelModesAre(self, chan, modes):
        self.DebugLog("OnChannelModesAre(", chan, modes, ")")
        
    def OnChannelModesChanged(self, chan, modes, nick):
        self.DebugLog("OnChannelModesChanged(", chan, modes, ")")
        
    def OnChannelUserModesChanged(self, chan, modes, by):
        self.DebugLog("OnChannelUserModesChanged(", chan, modes, by, ")")

    def IsConnected(self):
        return self.irc_connected

    def OnInterrupt(self):
        """Called when the mainloop is interrupted with a KeyboardInterrupt. Return True to continue execution."""
        return False
        
    #
    # Actions
    #

    def WrapLine(self, start, contents):
        ml = self.max_line_len - 2
        if len(start+contents) <= ml:
            return [start+contents]
        
        chunk = contents
        lines = []
        while 1:
            line = start + chunk
            print line
            if len(line) > ml:
                chunk = line[ml:]
                line = line[:ml]

                lines.append(line)
            else:
                lines.append(line)
                break
        return lines
    
    def PingServer(self):
        self.SendLine("PING " + self.current_nick)
        self.pinged_server = time.time()

    def ChangeNick(self, nick=None):
        self.DebugLog("Changing nick to:", nick)
        if nick == None:
            nick = self.def_nick
        self.SetNick(nick)
        self.SendLine("NICK %s" % nick)
      
    def DoIntroduce(self, nick=None, ident=None, realname=None):   # Send NICK and USER messages
        self.DebugLog("Introducing as:", "nick:", nick, ", ident:", ident, ", realname:", realname)
        if nick == None:
            nick = self.def_nick
        if ident == None:
            ident = self.def_ident
        if realname == None:
            realname = self.def_realname
        self.ChangeNick(nick)
        self.SendLine("USER %s 8 * :%s" % (ident, realname))
      
    def DoWhois(self, nick):
        self.SendLine("WHOIS %s %s" % (nick, nick))
      
    def JoinChannels(self, chans, keys=[]):
        if type(chans) in [type(u""), type("")]:
            chans = [chans]
        chanlist = ",".join(chans)
        keylist = ",".join(keys)
        self.SendLine("JOIN %s %s" % (chanlist, keylist))

    def Join(self, chans, keys=[]):
         self.JoinChannels(chans, keys)
        
    def PartChannels(self, chans):
        if type(chans) in [type(u""), type("")]:
            chans = [chans]
        chanlist = ",".join(chans)
        self.SendLine("PART %s" % chanlist)

    def Kick(self, chan, nick, message=""):
        self.SendLine("KICK %s %s %s" % (chan, nick, message))

    def Privmsg(self, dest, msg):
        if not msg:
            return False
        lines = self.WrapLine(u"PRIVMSG " + dest + u" :",msg)
        self.SendLines(lines)

    def Notice(self, dest, msg):
        if not msg:
            return False
        self.SendLine(u"NOTICE " + dest + u" :" + msg)

    def SetChannelUserModes(self, chan, nickmodes, operation=True):
        if operation:
            modes = "+"
        else:
            modes = "-"
        nicks = []
        for item in nickmodes:
            nicks.append(item[0])
            modes += item[1]
        self.SendLine(u"MODE " + chan + " " + modes + " " + (" ".join(nicks)))
     
    def SetChannelTopic(self, chan, topic):
        self.SendLine("TOPIC " + chan + " :" + topic)

    def SetChannelModes(self, chan, modes):
        self.SendLine("MODE " + chan + " " + modes)
      
    #
    # Protocol Implementation & Parsing
    #      
      
    # Returns the last (multi-word) parameter in the line, or False if not present
    def GetTextData(self, line):
        line = line[1:]
        index = line.find(":")
        if index != -1:
            return line[index+1:]
        else:
            return False
      
    def GetCleanNick(self, nick):
        if self.GetModeChr(nick) != IRC_MODE_CHR_NONE:
            return nick[1:]
        return nick
        
    def GetModeChr(self, s):
        if s[:1] in [IRC_MODE_CHR_VOICE, IRC_MODE_CHR_OP]:
            return s[:1]
        return IRC_MODE_CHR_NONE

    def IsChannelName(self, name):
        if name[0] in ["#", "&", "!"]:
            return True
        return False
        
    def GetMode(self, s):
        modechr = self.GetModeChr(s)
        if modechr == IRC_MODE_CHR_NONE:
            return None
        elif modechr == IRC_MODE_CHR_OP:
            return IRC_MODE_OP
        elif modechr == IRC_MODE_CHR_VOICE:
            return IRC_MODE_VOICE
      
    def ParseNickHost(self, line):
        part = line.split(" ")[0][1:]

        ind=part.find("!")
        if ind!=-1:
            nick = part[:ind]
            hostname = part[ind+1:]
        else:
            nick = ""
            hostname = part[1:]
        if nick != "":
            self.OnUserHostname(nick, hostname)
        return nick, hostname
      
    def LineIsCommand(self, line):
        cmds = ["ping", "pong", "join", "part", "kick", "topic", "quit", "privmsg", "nick", "mode", "notice"]
        parts = string.split(line)
        if len(parts) < 2:
            return False
        if parts[1].lower() in cmds:
            return True
        return False
        
    def LineIsNumeric(self, line):
        parts = string.split(line)
        if len(parts) < 2:
            return False
        try:
            numeric = int(parts[1])
            return True
        except:
            return False
      

    # Warning: Heavy shit (There be Dragons!)
    # ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====
    # Tries to parse a line received from the server
    def ParseLine(self, line):
        
        parts = string.split(line)
        txt_data = self.GetTextData(line)
        first_word = parts[0].lower()
                
        if first_word in ["ping", "error", "notice"]:
            if first_word == "ping":
                self.OnPing(" ".join(parts[1:]))
            elif first_word == "pong":
                pass
            elif first_word == "error":
                #ERROR :Closing Link: botti by portlane.se.quakenet.org (G-lined)
                #ERROR :Your host is trying to (re)connect too fast -- throttled
                text = line.lower()
                if text.find(":closing link:") != -1:
                    self.OnConnectThrottled(txt_data)
                elif text.find("throttled") != -1:
                    self.OnConnectThrottled(txt_data)
                elif text.find("g-lined") != -1:
                    self.OnConnectThrottled(reason)
            else:
                return False
                
        elif self.LineIsCommand(line):
            command = parts[1].lower()
            nick, hostname = self.ParseNickHost(line)

            if not command in ["pong", "ping"]:
                self.DebugLog("RAW:", line)

            if command == "pong":
                self.OnPing(txt_data)
            elif command == "join":
                if txt_data != False:
                    target = txt_data
                else:
                    target  = parts[2]
                nick, hostname = self.ParseNickHost(line)
                if nick == self.current_nick:
                    self.OnIJoined(target)
                else:
                    self.OnChannelJoin(target, nick)
            elif command == "part":
                if txt_data != False:
                    target = txt_data
                else:
                    target  = parts[2]
                nick,hostname = self.ParseNickHost(line)
                self.OnChannelPart(target, nick, txt_data)
            elif command == "topic":
                target  = parts[2]
                nick,hostname = self.ParseNickHost(line)
                topic = self.GetTextData(line)
                self.OnChannelTopicChanged(target, nick, topic)

            elif command == "privmsg":
                target  = parts[2]
                nick,hostname = self.ParseNickHost(line)
                self.OnPrivmsg(nick, target, txt_data)
            elif command == "notice":
                target  = parts[2]
                nick, hostname = self.ParseNickHost(line)
                if nick:
                    self.OnNotice(nick, target, txt_data)
            elif command == "quit":
                reason = self.GetTextData(line)
                nick, hostname = self.ParseNickHost(line)
                self.OnUserQuit(nick, reason)
            elif command == "kick":
                nick, hostname = self.ParseNickHost(line)
                target  = parts[2]
                who = parts[3]
                reason = self.GetTextData(line)
                self.OnChannelKick(target, who, nick, reason)
            elif command == "nick":
                newnick = self.GetTextData(line)
                nick, host = self.ParseNickHost(line)
                self.OnUserNickChange(nick, newnick)
            elif command == "mode":
                #self.DebugLog("\t\tParseLine(", line, ")")
                target = parts[2]
                if target == self.current_nick:
                    modes = parts[3]
                    self.OnMyModesChanged(modes)
                else:
                    types = ["-", "+"]
                    modes = parts[3]
                    
                    if len(parts) > 4:      # Channel user modes are being set
                        nicks = parts[4:]
                        i = 0
                        operation = True
                        users = []
                        for mode in modes:
                            char = modes[i]
                            if char in types:
                                if char == "-": operation = False
                                elif char == "+": operation = True
                                modes = modes[1:]
                                continue
                            modechr = modes[i]
                            user = (nicks[i], modechr, operation)
                            users.append(user)
                            i += 1
                        self.OnChannelUserModesChanged(target, users, nick)
                    else:
                        modes = parts[3]
                        self.OnChannelModesChanged(target, modes, nick)
            else:
                #self.DebugLog("\t\tParseLine(", line, ")","unknown text cmd")
                return False


        elif self.LineIsNumeric(line):
            numeric = int(parts[1])
            if numeric in [1, 2, 3]:      # Welcome info
                self.OnWelcomeInfo(txt_data)
            elif numeric == 4:
                self.OnWelcomeInfo(" ".join(parts[3:]))
            elif numeric == 5:
                self.OnSupportInfo(" ".join(parts[3:]))
            elif numeric == 20:
                self.OnProcessConn(txt_data)
            elif numeric == 42:
                self.OnYourId(parts[3], txt_data)
            elif numeric in [251, 252, 253, 254, 255]:
                self.OnServerInfo(" ".join(parts[3:]))
            elif numeric in [265, 266]:    # Local and global users
                #:no.address 265 bx 4 11 :Current local users 4, max 11
                #:no.address 266 bx 4 11 :Current global users 4, max 11
                pass # Implement if needed
            elif numeric in [311]:         # Parse whois responses
                nick = parts[3]
                if numeric == 311:
                    hostname = parts[4] + "@" + parts[5]
                    self.OnWhoisHostname(nick,hostname)
                
            elif numeric in [375, 372]:      # Start of MOTD, First line of MOTD
                self.OnMotdLine(txt_data)
            elif numeric in [376, 422]:    # End of MOTD, No MOTD
                self.OnReady()
            elif numeric in [324, 329, 332, 333, 353, 366, 473]:  # Channel numerics
            
                # Channel specific stuff
                chan = parts[3]
                
                if numeric in [324, 329]:
                    value = parts[4] 
                    if numeric == 329:                                  # channel creation time
                        self.OnChannelCreated(chan, value)
                    elif numeric == 324:                                # channel modes
                        modes = list(value.replace("+", ""))
                        self.OnChannelModesAre(chan, modes)
                        
                elif numeric == 332:                                    # channel topic
                    topic = self.GetTextData(line)
                    self.OnChannelTopicIs(chan, topic)
                    
                elif numeric == 333:                                    # channel topic metadata
                    nick = parts[4]
                    utime = int(parts[5])
                    self.OnChannelTopicMeta(chan, nick, utime)
                    
                elif numeric == 353:                                    # Reply to NAMES
                    chan = parts[4]
                    nicks = self.GetTextData(line).split(" ")
                    users = []
                    for raw_nick in nicks:
                        nick = self.GetCleanNick(raw_nick)
                        mode = self.GetMode(raw_nick)
                        users.append( (nick, mode) )
                    self.OnChannelHasUsers(chan, users)
                elif numeric == 366:                                    # End of NAMES
                    pass
                elif numeric == 473:                                    # Channel is invite only
                    self.OnChannelInviteOnly(chan, txt_data)
                elif numeric == 475:
                    self.OnChannelNeedsPassword(chan, txt_data)
            elif numeric == 433:                                        # Nick in use
                nick = parts[3]
                self.OnNickInUse(nick,txt_data)
            elif numeric == 465:
                self.OnConnectThrottled(txt_data)
            else:
                #self.DebugLog("\t\tParseLine(", line, ")", "unknown numeric")
                self.DebugLog("RAW:", line, "[unknown numeric]")
                return False
        else:
            self.DebugLog("RAW:", line, "[parsefail]")
            return False
    # ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====  
      

    #
    # Receive
    #
    
    def DataEncode(self, data):
        return data.encode(self.encoding)

    def DataDecode(self, data):
        for enc in self.decodings:
            try:
                return data.decode(enc)
            except Exception, err:
                continue
        return safe_escape(data)
        
    def ReceiveToBuffer(self):
        try:
            received = self.sock.recv(self.read_chunk_size)
        except socket.timeout, e:
            err = e.args[0]
            self.DebugLog("ReceiveToBuffer()", "timed out")
            if err == "timed out":
                return True
        except socket.error, e:
            self.DebugLog("ReceiveToBuffer()", "failed sock.recv", e)
            return False
        if len(received) == 0:
            self.DebugLog("ReceiveToBuffer()", "received empty data")
            return False

        if received:
            data = self.DataDecode(received)
            self.raw_buffer = self.raw_buffer + data
            lines = string.split(self.raw_buffer, "\n")
            self.raw_buffer = lines.pop()
            for line in lines:
                line = string.rstrip(line)
                self.recv_buffer.append(line)
                self.OnReceive(line)
            self.last_receive = time.time()
            self.pinged_server = False
            return True
        self.DebugLog("ReceiveToBuffer()","received nothing, sock dead?!")
        return False

    def ProcessRecvBuffer(self):
        if self.recv_buffer == []:
          return False
        line = self.recv_buffer.pop(0)
        self.ParseLine(line)

    #
    # Send
    #
            
    def Send(self, data):
        data = self.DataEncode(data)
        self.send_buffer.append(data)

    def LoopingSend(self, data):
        left = data
        while left != "":
            try:
                sent = self.sock.send(left)
                if len(left) == sent:
                    return True
                left = left[sent:]
            except:
                return False

    def ProcessSend(self, data):
        """This is where data to be sent finally ends up."""
        if self.irc_running & self.irc_connected:
            try:
              returned = self.LoopingSend(data)
              return True
            except Exception,e:
              self.DebugLog("ProcessSend", "fail:",data,e)
              return False
        else:
            self.DebugLog("ProcessSend", "not running & connected -> can't send!")
            return False
            
    def SendLines(self, lines):
        for line in lines:
            self.SendLine(line)
        
    def SendLine(self, line):            # Send one line to the server via the send buffer. FIXME CANT BE MORE THAN 512 CHARS LONG
        if len(line) > 510:
            self.DebugLog("SendLine(): line too long!")
        self.Send(line + "\r\n")

    def SendRaw(self, line):            # Send one line to the 
        self.SendLine(line)
        
    def ProcessSendBuffer(self):        # send line from buffer if not throttled
        if self.send_buffer != []:
            if self.send_time == None or time.time() - self.send_time > self.send_throttling:
                line = self.send_buffer.pop(0)
                if not self.ProcessSend(line):
                    return False
                self.send_time = time.time()
        else:
            return None

    def DropSendBuffer(self):
        self.send_buffer = []

    #
    # Start & Maintain Connection
    #

    def Connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if "settimeout" in dir(self.sock):
            self.sock.settimeout(self.sock_timeout) # This needs to be stoppable
        self.DebugLog("Connecting to " + self.host + ":" + str(self.port) + "...")
        try:
            self.sock.connect((self.host, self.port))
        except socket.error, err:
            self.DebugLog("Error connecting:", str(socket.error), str(err))
            return False
        self.irc_connected = 1
        return True
        
    def DelayReconnect(self):
        self.DebugLog("DelayReconnect()")
        time.sleep(self.throttle_wait)
        
    def Disconnect(self):
        self.irc_connected = 0
        self.irc_running = 0
        if self.sock != None:
            self.sock.close()
        self.InitializeClient()
        self.OnDisconnected()

    def KeepAlive(self):
        if self.last_receive != None:
            elapsed = time.time() - self.last_receive
        else:
            return
        # Ping the server after inactivity and wait for reply.
        # If no timely response is received, cut the connection and reconnect.
        if elapsed > self.max_inactivity:
            self.DebugLog("KeepAlive()", "server not responding to ping, reconnecting.")
            self.Disconnect()
        elif (not self.pinged_server) and elapsed > self.ping_after:
            self.PingServer()

    def Process(self):
        try:
           self.ProcessRecvBuffer()
           self.KeepAlive()
        except Exception, e:
            try:
                import traceback
                print traceback.format_exc()
            except:
                pass
            print sys.exc_info()[0]
            self.DebugLog("Process()", e)

    def IRCMaintain(self):
        try:
            self.OnLoop()
            try:
                sockl = [self.sock]
                if not s60:
                    readable, writable, errored = select.select(sockl, sockl, sockl, self.select_timeout)
                else:
                    readable, writable, errored = select.select(sockl, [], [], self.select_timeout)
                time.sleep(self.select_timeout)
            except socket.error, err:
                self.DebugLog("IRCMainloop()","select error:",socket.error,err)
                return False
            if self.sock in readable:
                ok = self.ReceiveToBuffer()     # Try to receive and break on failure
                if not ok:                      # If no data received, sock is dead
                    self.Disconnect()
                    return False
                return True
            elif self.sock in errored:
                self.DebugLog("IRCMainloop()","socket errored")
                return False
            elif self.sock in writable or s60:
                ok = self.ProcessSendBuffer()   # Try to send and break on failure
                if ok == False:
                    return False
            else:
                self.DebugLog("IRCMainloop()","socket inaccessible")
            self.Process()
            return True
        except KeyboardInterrupt:
            return self.OnInterrupt()
            # if self.OnInterrupt() == False:
                # return False
            # return True

    def IRCMainloop(self):
        while self.irc_running:
            result = self.IRCMaintain()
            if not result:
                return False

    # Connect and run irc client
    def StartClient(self, block=True):
        self.DebugLog("Starting client...") 
        connected = self.Connect()
        if connected:
            self.OnConnected()
            self.connection_time = time.time()
            self.irc_running = 1
            if block:
                status = self.IRCMainloop()
                self.InitializeClient()
                return status
            else:
                return True
        else:
            return False

    # Cut connection and stop
    def StopClient(self):
        self.DebugLog("StopClient()")
        self.irc_running = 0
        self.Disconnect()
        self.InitializeClient()
