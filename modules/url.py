# -*- coding: utf-8 -*-

from mod_base import * 

# Get <title> of web page
def get_url_title_new(url):
        print "Invalid extension: " + url[-3:]
    if url[-3:] in ["jpg", "png", "gif",]:
        return False
    # try:
    if urllib2 != False:
        u = urllib2.urlopen(url, timeout=5)
    else:
        u = urllib.urlopen(url)
    data = u.read()
    try:
        data = data.decode("utf-8")
    except:
        print "unable to decode url title as utf-8"
# except Exception,e:
    # return False

    # Find title ignoring tag case
    titleRE = re.compile("<title>(.+?)</title>", re.IGNORECASE)
    title = titleRE.search(data)
    if title == None:
        return False
    title = title.group(1)

    try:
        import HTMLParser
        hp = HTMLParser.HTMLParser()
        title = hp.unescape(title)
    except Exception, e:
        print "failed unescape entities with HTMLParser"
        title = title.replace("&auml;", u"ä")
        title = title.replace("&ouml;", u"ö")
        title = title.replace("&amp;", u"&")

    return title

class Url(Listener):
    """Find links in messages and post link titles when found."""
    def init(self):
        self.events = [IRC_EVT_MSG, IRC_EVT_CHAN_MSG]

    def event(self, event):
        # FIXME: find multiple urls at once
        urls = find_urls(event.msg)
        if urls != []:
            title = get_url_title_new(urls[0])
            if title != False:
                event.win.Send('"' + title + '"')

module = {
    "class": Url,
    "type": MOD_LISTENER,
    "zone": IRC_ZONE_BOTH,
}
