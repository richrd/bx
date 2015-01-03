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

def find_title(data):
    title = False
    try: # Try to use HTMLParser
        from HTMLParser import HTMLParser
        class TitleParser(HTMLParser):
            def __init__(self):
                HTMLParser.__init__(self)
                self.title = ""
                self.in_title = False

            def handle_starttag(self, tag, attrs):
                if tag == "title":
                    self.in_title = True

            def handle_endtag(self, tag):
                if self.in_title:
                    self.in_title = False
                    self.title = self.title.replace("\n", "")
                    self.title = self.title.replace("\r", "")

            def handle_data(self, data):
                if self.in_title:
                    self.title += data

        # instantiate the parser and fed it some HTML
        parser = TitleParser()
        parser.feed(data)
        title = parser.title or false

    except: # Fall back on regex
        titleRE = re.compile("<title>(\\s.*?)</title>", re.IGNORECASE)
        the_title = titleRE.findall(data)
        if the_title:
            title = the_title[0]
    if title:
        return title.strip()
    return False

# Get <title> of web page
def get_url_title(url, logf):
    ignore_ext = ["jpg", "png", "gif", "tiff", "psd", "zip", "rar", "sh"]
    if url[-3:] in ignore_ext:
        logf("Invalid extension.")
        return False

    # Check that the the resource content type is something relevant
    try:
        content_type = get_content_type(url)
        if content_type and not content_type in ["text/html", "text/xhtml", "text/plain"]:
            logf("Invalid content-type.")
            return False
    except:
        pass

    try:
        if urllib2 != False:
            u = urllib2.urlopen(url, timeout=5)
        else:
            u = urllib.urlopen(url)
    except:
        return False
    if u.getcode() != 200: # Only proceed if request is ok
        logf("Invalid response code.")
        return False

    # Read max 50 000 bytes to avoid Out of Memory
    data = u.read(50000)
    #logf(data)
    try:
        data = data.decode("utf-8")
    except:
        pass

    logf("Got url data.")
    title = find_title(data)
    if not title:
        return False
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
#<<<<<<< HEAD
#        if urls != []:
#            title = get_url_title_new(urls[0])
#=======
        titles = []
        for url in urls:
            title = get_url_title(url, self.Log)
#>>>>>>> 71c025ceeee47d288c62f986b24b8df6ec022f0a
            if title:
                titles.append('"'+title+'"')
        if titles:
            event.win.Send(", ".join(titles))

module = {
    "class": Url,
    "type": MOD_LISTENER,
    "zone": IRC_ZONE_BOTH,
}
