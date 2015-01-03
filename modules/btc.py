# -*- coding: utf-8 -*-

from mod_base import *
import time, json

class BTC(Command):
    """Display the current Bitcoin exchange rate. Default exchange is bitstamp. Usage: btc [exchange]"""
    def init(self):
        self.exchanges = {
            "bitstamp": "https://www.bitstamp.net/api/ticker/",
            "coinbase": "https://api.coinbase.com/v1/prices/spot_rate",
            "okcoin": "https://www.okcoin.com/api/ticker.do?ok=1",
            "lakebtc": "https://www.lakebtc.com/api_v1/ticker",
        }
        self.cache_max_age = 60*10   # cache results for 2 minutes
        self.cache = {}

    def get_url_data(self, url):
        try:
            u = urllib.urlopen(url, timeout=5)
            data = u.read()
            u.close()
            return data
        except:
            return False

    def get_rate(self, exchange):
        """Gets the exchange rate as USD from given exchange, and caches results."""
        if exchange in self.cache.keys():
            if time.time() + self.cache[exchange][0] > self.cache_max_age:
                return self.cache[exchange][1]
        data = self.get_url_data(self.exchanges[exchange])
        try:
            obj = json.loads(data)
        except:
            return False
        rate = False
        if exchange == "bitstamp":
            rate = obj["vwap"]
        elif exchange == "coinbase":
            rate = obj["amount"]
        elif exchange == "okcoin":
            rate = obj["ticker"]["buy"]
        elif exchange == "lakebtc":
            rate = obj["USD"]["ask"]

        self.cache[exchange] = (time.time(), rate)
        return rate

    def run(self, win, user, data, caller=None):
        args = Args(data)
        exchange = "bitstamp"
        if len(args) > 0:
            if args[0].lower() in self.exchanges.keys():
                exchange = args[0].lower()
            else:
                win.Send("Couldn't find that exchange.")
                return False

        rate = self.get_rate(exchange)
        if not rate:
            win.Send("oh noes, exchange rate unavailable")
            return False
        win.Send(str(rate) + " USD/BTC @ " + exchange)

module = {
    "class": BTC,
    "type": MOD_COMMAND,
    "level": 0,
    "zone":IRC_ZONE_BOTH,
}