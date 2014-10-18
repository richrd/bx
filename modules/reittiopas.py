# -*- coding: utf-8 -*-
from mod_base import *

import urllib, json
import sys
import datetime

class Reittiopas(Command):
    """Get public transport routes via www.reittiopas.fi. Usage: reittiopas start_address - end_address"""
    def init(self):
        self.base_url = "http://api.reittiopas.fi/hsl/prod"
        self.user = "Richrd"
        self.pwd = "hh8c9rny"
        self.debug = 1

    def parse_line_code(self, code):
        code = code[1:5]
        while code[0] == "0":
            code = code[1:]
        return "(" + code.strip() + ")"

    def parse_name(self, name):
        if name == None: return "[empty]"
        else: return name

    def parse_start_time(self, obj):
        t = obj[0]["depTime"][-4:]
        t = t[:2]+":"+t[2:]
        return "["+t+"]"

    def get_duration_str(self, sec):
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        data = ""
        if h:
            data = "%dh " % h
        return data + "%dm" % m

    def get_distance_str(self, m):
        m = int(m)
        s = str(m) + "m"
        if m > 1000:
             s = str(round(m/1000.0, 1)) + "km"
        return s

    def get_url(self, url):
        try:
            try:
                response = urllib.request.urlopen(url,
                    headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36"
                        }
                    )
            except:
                response = urllib.urlopen(url)
        except:
            return False
        data = response.read()    # a `bytes` object in python 3
        text = data
        return text

    def get_data(self, options):
        opts = {"user": self.user, "pass": self.pwd}
        opts.update(options)
        query = urllib.urlencode(opts)
        url = self.base_url+"?"+query
        text = self.get_url(url)
        if not text:
            print "Failed to get valid data."
            return False
        obj = json.loads(text)
        return obj


    def addr_to_coords(self, address):
        options = {
            "request": "geocode",
            "key": address,
            "loc_types": "address",
        }
        return self.get_data(options)

    def route_to_str(self, route, start, end):
        route = route[0]
        data = "Route " + self.get_duration_str(route["duration"]) + " " + self.get_distance_str(route["length"]) + ": "
        i = 0
        for node in route["legs"]:
            s = ""
            if node["type"] != "walk":
                s += self.parse_start_time(node["locs"]) + " "
                s += self.parse_line_code(node["code"])# + " "
            else:
                s += self.parse_start_time(node["locs"]) + " walk "
                s += self.get_distance_str(node["length"])# + " "
            if node["locs"][0]["name"]:
                s += " " + node["locs"][0]["name"]
            if node["locs"][-1]["name"]:
                s += " -> " + node["locs"][-1]["name"]
            else:
                s += " -> " + end
            if i != len(route["legs"])-1:
                s += ", "

            data += s
            i += 1
        return data

    def get_routes(self, start, end):
        obj1 = self.addr_to_coords(start)
        obj2 = self.addr_to_coords(end)
        addr1 = obj1[0]["coords"]
        addr2 = obj2[0]["coords"]

        options = {
            "from": addr1,
            "to": addr2,
            "request": "route",
        }
        return self.get_data(options)

    def run(self, win, user, data, caller=None):
        if not data or not data.find("-"):
            win.Send("Please provide start and end address: from - to")
            return False
        start, end = data.split("-")
        obj = self.get_routes(start, end)
        d = datetime.datetime.now()
        for route in obj:
            route_str = self.route_to_str(route, start, end)
            win.Send(route_str)

module = {
    "class": Reittiopas,
    "type": MOD_COMMAND,
    "level": 0,
    "zone": IRC_ZONE_BOTH
}