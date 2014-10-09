# -*- coding: utf-8 -*-
"""helpers.py: Various Helper Functions

Handles all neccessary parts of the irc protocol for client connections.

"""

import os
import sys
import time
import re
import urllib

try:
    import urllib2
except:
    urllib2 = None  # Legacy support

# Try to convert to string with a crude 'brute force' fall back
def safe_escape(text):
    try:
        return str(text)
    except:
        pass

    new = ""
    for c in text:
        try:
            new += unicode(str(c))
        except:
            new += "?"
    return new

# Convert value to string if necesary 
def arg_to_str(arg):
    if type(arg) in [type(""), type(u"")]:
        return arg
    else:
        return str(arg)

# Get a substring of a string with two delimeters
def get_string_between(start, stop, s):
        i1 = s.find(start)
        if i1 == -1:
            return False
        s = s[i1 + len(start):]
        i2 = s.find(stop)
        if i2 == -1:
            return False
        s = s[:i2]
        return s

# Get path to folder containing the current script
def get_current_script_path():
    return os.path.dirname(os.path.realpath(__file__))
        
# Convert times (add days, hours, min, sec)
def str_to_seconds(txt):
    units = {
        "d": 24*60*60,
        "h": 60*60,
        "m": 60,
        "s": 1,
        }
    txt = txt.strip().lower()
    if len(txt) < 2:
        return False
    if txt[-1] in units.keys():
        unit = units[txt[-1]]
    else:
        return False
    try:
        part = txt[:-1].replace(",", ".")
        n = float(part)
    except:
        return False

    return n*unit

# return human readable timestamps
def time_stamp(t=None, formatting=None):
    t = t or time.time()
    if not formatting:
        return time.asctime(time.localtime(float(t)))
    return time.strftime(formatting, time.localtime(float(t)))

def time_stamp_short(t=None):
    t = t or time.time()
    return time.strftime("%H:%M:%S", time.localtime(t))
    
def time_stamp_numeric(t=None):
    t = t or time.time()
    return time.strftime("%d.%m.%y %H:%M", time.localtime(t))
    
# run a shell command
def run_shell_cmd(cmd):
    try:
        import commands
    except:
        return False
    output = commands.getoutput(cmd)
    return output
        
# check if string contains a word
def has_word(s, w):
    words = re.split('\W+',s)
    if w in words:
        return True
    return False

# split string into words
def split_words(s):
    return re.split('\W+',s)

# find any urls in a string
def find_urls(s):
    try:
        re
    except:
        return []
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', s)
    return urls
