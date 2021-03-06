import urlparse
import urllib2
import ssl
from bs4 import BeautifulSoup
import re
import os.path
import Util
import pickle
import datetime
from WikiPage import WikiPage
import sys

begin = datetime.datetime.now()

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

reload(sys)
sys.setdefaultencoding('utf8')

prefix = "https://en.wikipedia.org/"
# start page
url = "https://en.wikipedia.org/wiki/Small-world_network"
path = os.path.dirname(os.path.abspath(__file__)) + '/files/'

urls = [url]
visited = [url]

count = 1
stop_expanding = False
max_pages = 5000

Util.deleteFilesFromFolder()

while ((len(urls) != 0) & (count <= max_pages)):
    print("COUNT", count)
    alreadyPop = False

    try:
        # get html page from url
        urllibObj = urllib2.urlopen(urls[0], context=ctx)
        html_text = urllibObj.read()

        # Removes saved html link from queue

        url = urls.pop(0)
        alreadyPop = True
        # if urllibObj.geturl() is not None:
        #     url = urllibObj.geturl()

        print("URL --------> ", url)

        soup = BeautifulSoup(html_text, "html.parser")
        title = str(soup.title.string)
        title = title[:len(title) - 12]
        # print wikipedia.page(title).content

        text = ""
        contents = soup.findAll('p')
        for content in contents:
            text = text + "\n" + content.text
        # print text

        # Expands actual url to find more non-visited urls
        bodyLinks = []
        paragraphs = soup.findAll('p')
        for paragraph in paragraphs:
            tags = paragraph.findAll('a', href=re.compile('^/wiki/'))
            for tag in tags:
                tag['href'] = urlparse.urljoin(url, tag['href'])
                if "cite_note" not in tag['href']:
                    bodyLinksUrl = [j[1] for j in bodyLinks]
                    if tag['href'] not in bodyLinksUrl:
                        bodyLinks.append((str(tag.string), tag['href']))
                        print tag['href'], str(tag.string)

                        if tag['href'] not in visited:
                            urls.append(tag['href'])
                            visited.append(tag['href'])

        # Categories assigned links
        print 'Categories'
        categories = set()
        links = soup.findAll('a', href=re.compile('^/wiki/Category'))
        for link in links:
            categories.add(str(links))
        print categories

        # Creating object (doc node)
        wikiPage = WikiPage(url, title, html_text, text, bodyLinks, categories)

        # Saving the object in a file
        file = path + str(count) + ".pkl"
        with open(file, 'wb') as output:
            pickle.dump(wikiPage, output, pickle.HIGHEST_PROTOCOL)
            count = count + 1

    except Exception, e:
        print("Error: " + url)
        print(e)
        if urls:
            if not alreadyPop:
                urls.pop(0)

end = datetime.datetime.now()
print("Time", str(end - begin))
