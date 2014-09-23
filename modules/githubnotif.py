from mod_base import *
import urllib2
import json

class GitHubNotifier(Listener):
    """Sends notification of new github commits to all channels"""
    def init(self):
        self.events = [IRC_EVT_INTERVAL]
        self.url = "https://api.github.com/repos/richrd/bx/events"
        self.user_agent = "richrd"
        self.api_data = None

    def GetNewCommits(self):
        if not self.api_data:
            self.api_data = self.GetData()
            return False
        else:
            new_data = self.GetData()
            new_items = self.FindNew(self.api_data, new_data)

            if not new_items:
                return False

            commits = []
            for item in new_items:
                messages = [commit["message"] for commit in item["payloads"]["commits"]]
                commits += messages
            return commits

    def FindNew(self, old, new):
        old_ids = [item["id"] for item in old]
        new_ids = [item["id"] for item in new]
        for i in old_ids:
            if i in new_ids:
                del new_ids[new_ids.index(i)]

        final = []
        for item in new:
            if new["id"] in new_ids:
                final.append(item)
        return final

    def GetData(self):
        req = urllib2.Request(self.url)
        req.add_header('User-agent', self.user_agent)
        resp = urllib2.urlopen(req)
        content = resp.read()
        api_data = json.loads(content)
        return api_data

    def SendNotification(self, new_items):
        for win in self.bot.windows:
            if win.zone == IRC_ZONE_CHANNEL:
                for item in new_items:
                    win.Send(self.ItemStr(item))

    def event(self, event):
        new_items = self.GetNewCommits()
        if new_items:
            self.SendNotification(new_items)


module = {
    "class": GitHubNotifier,
    "type": MOD_LISTENER,
    "zone": IRC_ZONE_CHANNEL,
    "interval": 60,
}