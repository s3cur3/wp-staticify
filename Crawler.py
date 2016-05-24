import errno

import os
import urllib.request
from bs4 import BeautifulSoup


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
                    out.add(policy.canonicalize(link.attrs["href"]))
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
        :type url: str
        :type html: str
        """
        def getLocalPathFromUrl(url):
            if url.endswith("/"):
                url += "index.html"
            return url


        if html and self.policy.shouldScrapeUrl(url):
            url = self.policy.canonicalize(url)
            path = self.policy.getOutDirectory() + os.sep + getLocalPathFromUrl(url)
            try:  # Create the parent directory
                os.makedirs(os.path.abspath(os.path.join(path, os.pardir)))
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise
            with open(path, "w") as f:
                f.write(self.policy.extractContent(html))

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
        with urllib.request.urlopen(req) as httpResponse:
            if httpResponse and httpResponse.headers["content-type"].startswith("text/"):
                return httpResponse.read().decode('utf-8')
            else:
                return ""


