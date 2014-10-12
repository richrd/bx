# -*- coding: utf-8 -*-
"""
Logging capabilities for the IRC Bot.
"""

import time
from helpers import *

LOG_NORMAL = "norm"
LOG_INFO = "info"
LOG_WARNING = "warn"
LOG_ERROR = "error"

class colors:
    BLACK = '\033[30m'
    GRAY = '\033[37m'
    GREEN = '\033[32m'
    MAGENTA = '\033[95m'
    VIOLET = '\033[95m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    DARKBLUE = '\033[34m'
    OKGREEN = '\033[92m'
    YELLOW = '\033[93m'
    ORANGE = '\033[33m'
    RED = '\033[91m'
    DARKRED = '\033[31m'
    ENDC = '\033[0m'


class Logger:
    def __init__(self, bot):
        self.bot = bot
        self.logs = []
        self.show_domains = ["irc", "bot", "cmd", "exc", "win", "user"]
        self.domain_colors = {
            "irc": colors.DARKBLUE,
            "bot": None,
            "cmd": colors.YELLOW,
            "exc": colors.RED,
            "win": colors.OKGREEN,
            "user": colors.MAGENTA,
        }
        self.show_types = [LOG_NORMAL, LOG_INFO, LOG_WARNING, LOG_ERROR]
        self.type_colors = {
            LOG_NORMAL: colors.BLUE,
            LOG_INFO: colors.GREEN,
            LOG_WARNING: colors.YELLOW,
            LOG_ERROR: colors.RED,
        }

    def Loaded(self):
        self.show_domains = self.bot.config["log_domains"]

    def ColorText(self, text, color):
        return color + text + colors.ENDC

    def RenderAll(self):
        for entry in self.logs:
            if entry[1] in self.show_types and entry[2] in self.show_domains:
                self.RenderLine(entry)

    def RenderLine(self, log_entry):
        line = time_stamp_short(log_entry[0])+" "

        type_color = self.type_colors[log_entry[1]]
        line += self.ColorText("[" + log_entry[1][0].upper() + "] ", type_color)

        domain = log_entry[2]
        log_str = log_entry[3]

        color = log_entry[4]
        if not color and domain in self.domain_colors.keys():
            color = self.domain_colors[domain]
        if color:
            line = line + color + log_str + colors.ENDC
        else:
            line = line + log_str

        print line

    def Log(self, domain, s, color=None, logtype = LOG_NORMAL):
        log_entry = [time.time(), logtype, domain, s, color]
        self.logs.append(log_entry)
        # print log_entry
        if log_entry[1] in self.show_types and log_entry[2] in self.show_domains:
            self.RenderLine(log_entry)


    def Info(self, domain, s, color=None):
        self.Log(domain, s, color, LOG_INFO)
        
    def Warning(self, domain, s, color=None):
        self.Log(domain, s, color, LOG_WARNING)

    def Error(self, domain, s, color=colors.RED):
        self.Log(domain, s, color, LOG_ERROR)
