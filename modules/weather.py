# -*- coding: utf-8 -*-
from mod_base import *
import time, json

class Weather(Command):
    """Display the current weather conditions. Usage: weather [location]"""
    def init(self):
        self.storage.Load()
        self.api_url_base = "http://api.openweathermap.org/data/2.5/weather?q=[[QUERY]]&units=metric&APPID="
        self.default_query = "helsinki"
        self.cache_max_age = 60*5   # cache results for 5 minutes
        # Queries are cached with city as dict key
        # Cache data is stored as (timestamp, data)
        self.cache = {}

    def get_url_data(self, url):
        try:
            u = urllib.urlopen(url)
            data = u.read()
            u.close()
            return data
        except:
            return False

    def get_weather_data(self, query):
        # Must use this encoding workaround (fixed in Python 3)
        query = query.encode("utf8")
        query = urllib.quote(query.lower().strip())
        url = self.api_url_base + self.storage["api_key"]
        url = self.api_url_base.replace("[[QUERY]]", query)
        if query in self.cache.keys() and time.time()-self.cache[query][0] < self.cache_max_age:
            return self.cache[query][1]
        else:
            data = self.get_url_data(url)
            try:
                data = json.loads(data)
                self.cache[query] = (time.time(), data)
                return data
            except:
                return False

    def run(self, win, user, data, caller=None):
        args = Args(data)
        query = self.default_query
        if not args.Empty():
            query = args.Range(0)
        wdata = self.get_weather_data(query)
        if not wdata:
            win.Send("Sorry, weather data can't be retrieved.")
            return False
        code = wdata["cod"]
        if code != 200:
            message = ""
            if "message" in wdata.keys():
                message = " (" + wdata["message"] + ")"
            win.Send("Sorry, weather unavailable." + message)
            return False

        stamp = wdata["dt"]
        weather = wdata["weather"][0]
        temp = str(wdata["main"]["temp"])
        humidity = str(wdata["main"]["humidity"])
        windspeed = str(wdata["wind"]["speed"])
        clouds = str(wdata["clouds"]["all"])
        place = wdata["name"]
        condition = weather["description"] + ", "
        output = condition + ", ".join([
                temp + u"\u00B0C",
                "wind speed " + windspeed + "m/s",
                "cloudiness " + clouds + "%",
                "humidity " + humidity + "%",
                "@ " + place,
                # time.strftime("[%b %d %Y %H:%M:%S GMT]", time.gmtime(stamp)) # debug cache
            ])
        win.Send(output)

module = {
    "class": Weather,
    "type": MOD_COMMAND,
    "level": 0,
    "zone":IRC_ZONE_BOTH,
    "storage": {
        "api_key": ""
    }
}
