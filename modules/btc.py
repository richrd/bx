# -*- coding: utf-8 -*-

from mod_base import *
import json

class BTC(Command):
    """Display the current Bitcoin exchange rate."""
    def init(self):
        self.exchanges = {
            "bitstamp": "https://www.bitstamp.net/api/ticker/",
        }
        self.cache_age = 60*10

    def get_url_data(self, url):
        try:
            u = urllib.urlopen(url, timeout = 5)
            data = u.read()
            u.close()
            return data
        except:
            return False

    def get_rate(self, exchange):
        data = self.get_url_data()

        try:
            obj = json.loads(data)
        except:
            return False

        if exchange == "bitstamp":
            return obj["vwap"]


        return False

    def run(self, win, user, data, caller=None):
        exchange = "bitstamp"
        rate = self.get_rate(exchange)
        if not rate:
            win.Send("oh noes, exchange rate unavailable")
            return False

        win.Send(rate + "USD/BTC (@" + exchange + ")")
        # line = rate+" EUR/BTC"
        # if mins>0:
        #     line=line+" ("+str(mins)+" mins ago @ "+self.exchange_name+")"
        # else:
        #     line=line+" (now @ "+self.exchange_name+")"
        # win.Send(line)


module = {
    "class": BTC,
    "type": MOD_COMMAND,
    "level": 0,
    "zone":IRC_ZONE_BOTH,
}