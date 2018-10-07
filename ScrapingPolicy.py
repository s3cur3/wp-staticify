from urllib.parse import urlparse

class ScrapingPolicy:
    def __init__(self, start_at_url):
        """
        :param start_at_url: The URL we should begin scraping with (typically your home page or a sitemap page)
        :type start_at_url: str
        """
        self.start_at_url = start_at_url
        self.uri = urlparse(start_at_url)
        assert self.uri.scheme in ('http', 'https')

    @property
    def max_concurrent_requests(self):
        return 20

    @property
    def domain(self):
        return f"{self.uri.scheme}://{self.uri.netloc}"

    def shouldCrawlUrl(self, url):
        """
        :type url: str
        :rtype: bool
        :return: true iff this URL should be crawled
        """
        return (self.domain in url or url.startswith('/')) and '/scenery/page/' not in url

    def shouldScrapeUrl(self, url):
        """
        :type url: str
        :rtype: bool
        :return: true iff this page should be scraped
        """
        return self.domain in url

    def canonicalize(self, url):
        """
        :type url: str
        :return: Canonical version of the URL in question, such that two pages with different paths don't get scraped twice.
                 Note that the canonical version should be an absolute URL (e.g., http://mysite.com/home/).
        :rtype: str

        >>> policy = ScrapingPolicy('http://foo.bar')
        >>> policy.canonicalize('http://foo.bar/baz')
        'http://foo.bar/baz/'

        >>> policy = ScrapingPolicy('http://foo.bar')
        >>> policy.canonicalize('http://foo.bar/baz/index.html')
        'http://foo.bar/baz/'
        """
        abs_url = self.domain + url if url.startswith('/') else url
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

    @property
    def out_directory(self):
        """
        :return: The directory into which we should write all the scraped content
        :rtype: str

        >>> policy = ScrapingPolicy('http://foo.bar')
        >>> policy.out_directory
        'foo.bar'
        """
        return self.uri.netloc


if __name__ == "__main__":
    import doctest
    doctest.testmod()

