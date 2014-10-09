# -*- coding: utf-8 -*-
"""
Logging capabilities IRC Bot.
"""

import time
from helpers import *

class colors:
    BLACK = '\033[30m'
    GRAY = '\033[37m'
    GREEN = '\033[32m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    DARKBLUE = '\033[34m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

class Logger:
    def __init__(self, bot):
        self.bot = bot
        self.logs = []
        self.domain_colors = {
            "irc": colors.DARKBLUE,
            "bot": None,
            "cmd": colors.WARNING,
            "win": colors.OKGREEN,
            "user": colors.MAGENTA,
        }

    def Log(self, domain, s, color=None):
        if not color and domain in self.domain_colors.keys():
            color = self.domain_colors[domain]
        self.logs.append([time.time(), domain, s, color])
        line = time_stamp_short()+" "+s
        if color:
            line = color + line + colors.ENDC
        print line

    def Warning(self, domain, s, color=None):
        self.Log(domain, s, colors.FAIL)