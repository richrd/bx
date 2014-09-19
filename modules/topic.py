from mod_base import*

class Topic(Command):
    """Change the channel topic. To add to the current topic, start your topic with a '+' symbol."""
    def run(self, win, user, data, caller=None):
        if data == None:
            win.SetTopic(" ")
            return False
        else:
            new_topic = data
            if data[0] == "+":
                new_topic = win.topic+" | "+data[1:]
            win.SetTopic(new_topic)

module = {
    "class": Topic,
    "type": MOD_COMMAND,
    "level": 2,
    "zone":IRC_ZONE_BOTH
}