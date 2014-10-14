# -*- coding: utf-8 -*-
# By Lauri Peltomäki, all rights given to the original author.
from mod_base import *
import time, json, httplib

class DOGECOIN(Command):
    """Display the current DogeCoin exchange rate, from bter. Usage: dogecoin"""
    def init(self):
        self.domain  = "data.bter.com"
        self.timeout = 10
        self.url     = "http://data.bter.com/api/1/ticker/doge_usd"

    def get_data(self):
        try:
            conn = httplib.HTTPSConnection(self.domain, timeout=self.timeout)
            # This is a must, bter requires it.
            headers = {"Content-type": "application/x-www/form/urlencoded"}
            conn.request("GET", self.url, "", headers)
            data = conn.getresponse().read()
            conn.close()
            return data
        except:
            return False

    def get_rate(self):
        """Get the exchange rate as USD."""

        data = self.get_data()

        try:
            obj = json.loads(data)
        except:
            return False

        rate = False
        rate = obj["last"]

        return rate

    def run(self, win, user, caller=None):
        rate = self.get_rate()
        if not rate:
            win.Send("Unacceptable! The exchange rate is unavailable!")
            return False
        win.Send(str(rate) + " USD/DOGE @ " + self.domain)

module = {
    "class": DOGECOIN,
    "type": MOD_COMMAND,
    "level": 0,
    "zone": IRC_ZONE_BOTH,
}
