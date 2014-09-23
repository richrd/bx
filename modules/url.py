from mod_base import*

class Url(Listener):
    """Find links in messages and post link titles when found."""
    def init(self):
        self.events = [IRC_EVT_MSG, IRC_EVT_CHAN_MSG]

    def event(self, event):
        # FIXME: find multiple urls at once
        urls = find_urls(event.msg)
        if urls != []:
            title = get_url_title(urls[0])
            if title != False:
                event.win.Send('"' + title + '"')

module = {
    "class": Url,
    "type": MOD_LISTENER,
    "zone": IRC_ZONE_BOTH,
}