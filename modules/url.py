# -*- coding: utf-8 -*-

from mod_base import * 


def get_mimetype(url):
    import httplib
    from urlparse import urlparse
    urlobj = urplarse(url)
    domain = urlobj.netloc
    get = urlobj.path + urlobj.query
    conn = httplib.HTTPConnection(domain, timeout=5)
    conn.request("HEAD", get)
    res = conn.getresponse()
    # print res.status, res.reason
    headers = res.getheaders()
    #[('content-length', '0'), ('expires', '-1'), ('server', 'gws'), ('cache-control', 'private, max-age=0'), ('date', 'Sat, 20 Sep 2008 06:43:36 GMT'), ('content-type', 'text/html; charset=ISO-8859-1')]
    content_type = False
    for item in headers:
        if item[0] == 'content-type':
            content_type = item[1].split(";")[0].strip()
            break
    return content_type

# Get <title> of web page
def get_url_title_new(url):
    ignore_ext = ["jpg", "png", "gif", "tiff", "psd", "zip", "rar", "sh"]
    if url[-3:] in ignore_ext:
        print "Invalid extension: " + url[-3:]
        return False

    # Check that the the resource content type is something relevant
    try:
        content_type = get_content_type(url)
        if content_type and not content_type in ["text/html", "text/xhtml", "text/plain"]:
            print "Invalid content type!", content_type
            return False
    except:
        pass


    if urllib2 != False:
        u = urllib2.urlopen(url, timeout=5)
    else:
        u = urllib.urlopen(url)
    data = u.read()
    
    try:
        data = data.decode("utf-8")
    except:
        print "unable to decode url title as utf-8"


    # Find title ignoring tag case
    titleRE = re.compile("<title>(.+?)</title>", re.IGNORECASE)
    title = titleRE.findall(data)
    if not title:
        return False
    title = title[0]

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
        print "url event"
        # FIXME: find multiple urls at once
        urls = find_urls(event.msg)
        print "got urls", urls
        titles = []
        for url in urls:
            title = get_url_title_new(url)
            if title != False:
                titles.append('"'+title+'"')
        print "titles:", titles
        if titles:
            event.win.Send(", ".join(titles))

module = {
    "class": Url,
    "type": MOD_LISTENER,
    "zone": IRC_ZONE_BOTH,
}
