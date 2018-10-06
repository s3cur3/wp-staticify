
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
        return self.rootUrl in url or url.startswith('/')

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
        :return: Canonical version of the URL in question, such that two pages with different paths don't get scraped twice.
                 Note that the canonical version should be an absolute URL (e.g., http://mysite.com/home/).
        :rtype: str
        """
        abs_url = self.rootUrl + url if url.startswith('/') else url
        components = abs_url.split('/')
        if components[-1]:  # if the path doesn't end in a /
            if components[-1] == 'index.html':
                components.pop()  # canonicalize /foo/bar/index.html as /foo/bar/
            if '.' not in components[-1]:  # last component is "just" a "slug" in WordPress terms, like /foo/bar, not /foo/bar.baz or /foo/bar/
                components.append('')  # give us a trailing slash!
            return '/'.join(components)
        return abs_url

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


