import errno

import os
import urllib.request
from bs4 import BeautifulSoup
from ScrapingPolicy import ScrapingPolicy  # for the sake of PyCharm's auto-documentation
from urllib.parse import urlparse

class Crawler:
    def __init__(self, policy):
        """
        :type policy: ScrapingPolicy
        """
        self.policy = policy

    def crawl(self):
        """
        Crawls the site and writes the scraped HTML (and images, etc.) to disk
        """
        def collectLinksToScrape(html, policy):
            """
            :type html: str
            :type policy: ScrapingPolicy
            :rtype: set[str]
            """
            soup = BeautifulSoup(html, "lxml")
            out = set()
            for link in soup.find_all("a"):
                if "href" in link.attrs and policy.shouldCrawlUrl(link.attrs["href"]):
                    href = policy.canonicalize(link.attrs["href"])
                    assert(href.startswith("http://"))
                    out.add(href)
            return out

        rootText = self.readText(self.policy.rootUrl)
        self.scrape(self.policy.rootUrl, rootText)

        toCrawl = collectLinksToScrape(rootText, self.policy)
        crawled = set()
        while toCrawl:
            url = toCrawl.pop()
            if url not in crawled:
                crawled.add(url)
                pageText = self.readText(url)
                self.scrape(url, pageText)
                for subUrl in collectLinksToScrape(pageText, self.policy):
                    if subUrl not in crawled:
                        toCrawl.add(subUrl)

    def scrape(self, url, html):
        """
        :param url: A canonical, absolute URL
        :type url: str
        :param html: The full HTML of the page for us to parse and write to disk
        :type html: str
        """
        if html and self.policy.shouldScrapeUrl(url):
            path = self.getLocalPathFromUrl(url)
            try:  # Create the parent directory
                os.makedirs(os.path.abspath(os.path.join(path, os.pardir)))
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
            with open(path, "w") as f:
                f.write(self.policy.extractContent(html))

    def getLocalPathFromUrl(self, canonicalUrl):
        parsedUrl = urlparse(canonicalUrl)
        assert (self.policy.rootUrl == '{uri.scheme}://{uri.netloc}/'.format(uri=parsedUrl))
        urlPath = parsedUrl.path  # ignore the domain
        if urlPath.endswith("/"):
            urlPath += "index.html"
        return self.policy.getOutDirectory() + os.sep + urlPath

    def readText(self, url):
        """
        If the URL represents a text page (e.g., HTML), returns the text we read from the page; else, returns the empty string
        :rtype: str
        """
        req = urllib.request.Request(
            url,
            data=None,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
        )
        try:
            with urllib.request.urlopen(req) as httpResponse:
                if httpResponse and httpResponse.headers["content-type"].startswith("text/"):
                    return httpResponse.read().decode('utf-8')
                else:
                    return ""
        except urllib.error.HTTPError:
            return ""


