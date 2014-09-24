# -*- coding: utf-8 -*-
"""mods.py: Module loader for the IRC bot.

Loader for commands and listeners.

TODO:
* Refactor<3
"""

import os
import sys
import time
import string
import random
import imp

# Symbian S60 specific compatibility
s60 = False
if sys.platform == "symbian_s60":
    s60 = True
    sys.path.append("e:\\python")
    sys.path.append("c:\\python")
    sys.path.append("c:\\DATA\\python")

from helpers import *
from const import *

import traceback
import urllib
import re

def LoadAll():
    dirlist = os.listdir("modules/")
    modules = {}

    writedocs = False
    docs = []

    for item in dirlist:
        module = LoadSingle(item)
        if module:
            name = module[0]
            mod = module[1]

            if "__doc__" in dir(mod["class"]):
                docs.append((name, mod["class"].__doc__))


            mod["name"] = name
            
            if not "aliases" in mod.keys():
                mod["aliases"] = []
            
            if not "throttle" in mod.keys():
                mod["throttle"] = None
            
            if not "interval" in mod.keys():
                mod["interval"] = None
            
            if not "zone" in mod.keys():
                mod["zone"] = IRC_ZONE_BOTH

            modules[module[0]] = module[1]

    if writedocs:
        docs.sort()
        s = ""
        for doc in docs:
            s += "*   " + doc[0] + "\n"
            parts = doc[1].split("\n")
            lines = ["    > "+line.strip() for line in parts if line.strip()]
            s += "\n".join(lines)
            s += "\n\n"
        f = open("mod_docs.txt","w")
        f.write(s)
        f.close()

    return modules

def LoadSingle(filename):
    if filename[0] == ".":
        return False
    parts = filename.split(".")
    if len(parts) < 2: return False
    name = parts[0]
    ext = parts[-1]

    # only load .py modules that don't begin with an underscore
    if ext == "py" and name[0] != "_":
        mod = imp.load_source(name, "modules/" + filename)
        return name, mod.module
    return False

modules = LoadAll()
