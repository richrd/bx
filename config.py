# -*- coding: utf-8 -*-
"""mods.py: Modules for the IRC bot.

Contains all built in commands and listeners.

"""

import mods
from helpers import *

# Legacy platforms
try:
    import json
except:
    json = None 


# md5 hex digest
def md5hd(data):
    try:
        import hashlib
        return hashlib.md5(data).hexdigest()
    except:
        try:
            import md5
            return md5.new("a").hexdigest()
        except:
            return None


class BotConfig:
    def __init__(self, bot, filename = None):
        self.bot = bot
        self.filename = filename
        self.config = {
                "server": {
                    "host": "localhost",
                    "port": 6667,
                },
                
                "throttle_wait":400,     # how long to/ wait before reconnecting after throttle (too many clones)
                "throttle_add":120,     # How many seconds to add after each consecutive throttle

                "nicks":[u"bx",],
                "nick_suffix":"_",
                "realname":"bx",
                "ident":"bx",
                "ignore_nicks":[],
                
                "default_send":"privmsg",
                "cmd_prefix":".",
                "cmd_throttle":1.5,
                
                "send_throttle":1.8,
                "default_log_limit":1000,
                "avoid_cmd_crash":True,
                
                "default_mods":"*",        # all mods enabled by default

                "channels":{    # names must be lower case!
                    "#bx-test":{
                        "modes":"stnCN",
                        },
                    },
                "accounts":{
                    "admin":
                        {
                        "name":"admin",
                        "level":5,
                        "pw":"some-md5-hash",
                        "hostnames":[               # Trusted hostnames
                            "~name@user.example.com",
                            ],
                        },
                    },
                "modules":{},
                }
        self.cmd2alias = {}
        self.aliases = {}
        
    def keys(self):
        return self.config.keys()
        
    def AccountExists(self, name):
        return name.lower() in self.config["accounts"].keys()

    def AddAccount(self, name, password):
        self.config["accounts"][name] = {
            "name": name,
            "pw": md5hd(password),
            "level": 1,
            "hostnames": []
        }
        return True

    def RemoveAccount(self, name):
        if name in self.config["accounts"].keys():
            del self.config["accounts"][name]
            return True
        return False

    def GetAccountByName(self, name):
        if name in self.config["accounts"].keys():
            return self.config["accounts"][name]
        return False

    def ChangeAccountPass(self, name, oldpass, newpass):
        if self.AccountExists(name):
            account = self.config["accounts"][name]
            oldhash = md5hd(u"" + oldpass)
            if oldhash == account["pw"]:
                account["pw"] = md5hd(u"" + newpass)
                return True
        return False

    def AddChannel(self, name):
        if not name in self.config["channels"].keys():
            self.config["channels"][name] = {}
            return True
        return False

    def RemoveChannel(self, name):
        if name in self.config["channels"].keys():
            del self.config["channels"][name]
            return True
        return False

    def GetChannels(self):
        return self.config["channels"].keys()

    def GetAutoJoinChannels(self):
        return self.GetChannels()

    def AuthenticateUser(self, name, pw):
        if self.AccountExists(name):
            account = self.config["accounts"][name]
            h = md5hd(u"" + pw)
            if h == account["pw"]:
                return account
        return False
        
    def AuthenticateHostname(self, hostname):
        for item in self.config["accounts"].items():
            account = item[1]
            if "hostnames" in account.keys() and hostname in account["hostnames"]:
                return account
        return False
        
    def RememberAccountHostname(self, name, hostname):
        if name in self.config["accounts"].keys():
            if hostname in self.config["accounts"][name]["hostnames"]:
                return False
            self.config["accounts"][name]["hostnames"].append(hostname)
            self.Store()
            return True
        else:
            return False
        
    def GetChannelModes(self, win):
        name = win.GetName().lower()
        if name in self.config["channels"]:
            if "modes" in self.config["channels"][name]:
                return self.config["channels"][name]["modes"]
            return None
        return None

    def GetMods(self, val=None):
        enabled = []
        if "*" in self.config["default_mods"]:
            enabled = mods.modules.keys()
        for part in self.config["default_mods"]:
            if part[0] == "-":
              if part [1:] in enabled:
                  enabled.pop(enabled.index(part[1:]))
        else:
            if part[0] == "+": part = part[1:]
            enabled.append(part)
        return enabled
	
    def ApplyModConfig(self, module):
        """Apply configuration options to a module dict and return it."""
        keys = ["throttle", "level", "zone", "aliases", "interval"]
        if module["name"] in self.config["modules"].keys():
            mod = self.config["modules"][module["name"]]
            for key in keys:
                if key in mod.keys():
                    module[key] = mod[key]  # Apply each existing value from config to module
        return module

    def DisableMod(self, mod):
        mod = mod.lower()
        if mod in self.config["default_mods"]:
            self.config["default_mods"].pop(self.config["default_mods"].index(mod))
        if not "-" + mod in self.config["default_mods"]:
	        self.config["default_mods"].append("-" + mod)
        self.Store()
      
    def EnableMod(self, mod):
        mod = mod.lower()
        if "-" + mod in self.config["default_mods"]:
            self.config["default_mods"].pop(self.config["default_mods"].index("-" + mod))
        if mod not in self.config["default_mods"]:
           self.config["default_mods"].append(mod)
        self.Store()

    def GetModule(self, modname):
        modname = modname.lower()
        if modname in self.config["modules"].keys():
            mod_conf = self.config["modules"][modname]
            mod_conf["name"] = modname
            return mod_conf
        return False

    def ModSet(self, modname, key, value):
        modname = modname.lower()
        if not modname in self.config["modules"].keys():
            self.config["modules"][modname] = {}
        self.config["modules"][modname][key] = value
        mod = self.bot.GetModule(modname)
        mod.SetProperties(self.config["modules"][modname])
        return True

    def UserSet(self, user, key, value):
        user = user.lower()
        if not user in self.config["accounts"].keys():
            self.config["accounts"][user] = {}
        self.config["accounts"][user]["level"] = value
        return True

    def AliasToCommand(self,alias):
        if alias in self.aliases:
            cmd = self.aliases[alias]
            return cmd
        return False

    def GetAliases(self, command):
        if command in self.cmd2alias:
            return self.cmd2alias[command]
        return False

    def Log(self,txt):
        self.bot.log.Log("config", txt)

    def Serialize(self):
        data = self.config
        if json != None:
            return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            return str(data)

    def UnSerialize(self,data):
        if json != None:
            return json.loads(data)
        return eval(data)

    def Store(self):
        if self.filename == None:
            self.Log("Store: no filename given")
            return False
        try:
            data = self.Serialize()
            f = open(self.filename,"w")
            f.write(data)
            f.close()
            return True
        except Exception,e:
            self.Log("Store: write failed:" + str(e))
            return False

    def LoadAliases(self):
        self.aliases = {}
        for name in mods.modules:
            module = mods.modules[name]
            module = self.ApplyModConfig(module)
            if module["aliases"]:
                for alias in module["aliases"]:
                    self.aliases[alias] = module["name"]
                self.cmd2alias[name] = module["aliases"]

    def LoadFile(self, filename):
        self.filename = filename
        load = self.Load()
        return load

    def Load(self):
        if self.TryLoad():
            self.LoadAliases()
            return True
        else:
            self.Log("Failed to read config. exiting.")
            exit

    def TryLoad(self):
        if self.filename == None:
            return False
        try:
            f = open(self.filename,"r")
            data = f.read()
            f.close()
            self.Log("Load: loaded "+self.filename)
        except Exception,e:
            self.Log("Load: read failed:"+str(e))
            return False
        if data != "":
            try:
                config = self.UnSerialize(data)
            except Exception,e:
                self.Log("Load: parsing config file failed:"+str(e))
                return False
            self.AppendLoadedConfig(config)
            return True
        return False

    # Add config without removing old entries
    def AppendLoadedConfig(self, conf):
        for key in conf.keys():
            self.config[key] = conf[key]
        self.FillIn()
            
    def FillIn(self):
        for name in self.config["accounts"].keys():
            if not "hostnames" in self.config["accounts"][name].keys():
                self.config["accounts"][name]["hostnames"] = []

    def __getitem__(self,attr):
        return self.config[attr]
    
    def __setitem__(self,attr,val):
        self.config[attr] = val
