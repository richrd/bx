# -*- coding: utf-8 -*-
from mod_base import *
import time, json

class Weather(Command):
    """Display the current weather conditions."""
    def init(self):
        self.api_key = "5d4f25ba8d50f6bd0a30e8f32560a669"
        self.api_url = "http://api.openweathermap.org/data/2.5/weather?q=[[QUERY]]&units=metric&APPID="+self.api_key
        self.default_query = "Helsinki,fi"
        self.cache_max_age = 60*2   # cache results for 2 minutes

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
        query = query.lower()
        url = self.api_url.replace("[[QUERY]]", query)
        if query in self.cache.keys() and time.time()-self.cache[query][0] > self.cache_max_age:
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
            query = args[0]

        wdata = self.get_weather_data(query)
        if not wdata:
            win.Send("Sorry, weather data can't be retrieved.")
            return False

        weather = wdata["weather"][0]
        temp = str(wdata["main"]["temp"]) # Convert from Kelvin to Celcius
        humidity = str(wdata["main"]["humidity"])
        windspeed = str(wdata["wind"]["speed"])
        clouds = str(wdata["clouds"]["all"])
        place = str(wdata["name"])

        condition = weather["description"] + ", "
        output = condition + ", ".join([
                temp + u"\u00B0C ",
                "wind speed " + windspeed + "m/s ",
                "cloudiness " + clouds + "% ",
                "humidity " + humidity + "%, ",
                "@ " + place
            ])
        win.Send(output)

"""
"{"coord":{"lon":24.94,"lat":60.17},
"sys":{"type":1,"id":5018,"message":0.0315,"country":"FI","sunrise":1412656885,"sunset":1412696071},
"weather":[{"id":800,"main":"Clear","description":"Sky is Clear","icon":"01n"}],"base":"cmc 
stations","main":{"temp":283.4,"pressure":1028,"humidity":62,"temp_min":282.95,"temp_max":284.15},
"wind":{"speed":7.2,"deg":110,"var_beg":70,"var_end":140},
"clouds":{"all":0},
"dt":1412700618,"id":658225,"name":"Helsinki","cod":200}
"""


module = {
    "class": Weather,
    "type": MOD_COMMAND,
    "level": 0,
    "zone":IRC_ZONE_BOTH,
}