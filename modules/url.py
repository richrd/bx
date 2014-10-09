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
    headers = res.getheaders()
    content_type = False
    for item in headers:
        if item[0] == 'content-type':
            content_type = item[1].split(";")[0].strip()
            break
    return content_type

# Get <title> of web page
def get_url_title(url):
    ignore_ext = ["jpg", "png", "gif", "tiff", "psd", "zip", "rar", "sh"]
    if url[-3:] in ignore_ext:
        return False

    # Check that the the resource content type is something relevant
    try:
        content_type = get_content_type(url)
        if content_type and not content_type in ["text/html", "text/xhtml", "text/plain"]:
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
        pass

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
        title = title.replace("&auml;", u"ä")
        title = title.replace("&ouml;", u"ö")
        title = title.replace("&amp;", u"&")

    return title

class Url(Listener):
    """Find links in messages and post link titles when found."""
    def init(self):
        self.events = [IRC_EVT_MSG, IRC_EVT_CHAN_MSG]

    def event(self, event):
        urls = find_urls(event.msg)
        titles = []
        for url in urls:
            title = get_url_title(url)
            if title != False:
                titles.append('"'+title+'"')
        if titles:
            event.win.Send(", ".join(titles))

module = {
    "class": Url,
    "type": MOD_LISTENER,
    "zone": IRC_ZONE_BOTH,
}
