
class ScrapingPolicy:
    def __init__(self, rootUrl):
        """
        :param rootUrl: The URL we should begin scraping with (typically your home page)
        :type rootUrl: str
        """
        self.rootUrl = rootUrl

    def shouldCrawlUrl(self, url):
        """
        :type url: str
        :rtype: bool
        :return: true iff this URL should be crawled
        """
        return self.rootUrl in url

    def shouldScrapeUrl(self, url):
        """
        :type url: str
        :rtype: bool
        :return: true iff this page should be scraped
        """
        return self.rootUrl in url

    def canonicalize(self, url):
        """
        :type url: str
        :rtype: str
        :return: canonical version of the URL in question, such that two pages with different paths don't get scraped twice
        """
        return url

    def extractContent(self, content):
        """
        Performs any filtering/transformations necessary to turn the full HTML contents of the page into the version you want to save (maybe stripping extraneous info?)
        :param content: The full HTML contents of the page
        :type content: str
        :rtype: str
        """
        return content

    def getOutDirectory(self):
        """
        :return: The directory into which we should write all the scraped content
        :rtype: str
        """
        return "out"


