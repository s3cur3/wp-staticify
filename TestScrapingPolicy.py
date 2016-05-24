from ScrapingPolicy import ScrapingPolicy


class TestScrapingPolicy(ScrapingPolicy):
    def __init__(self):
        super(TestScrapingPolicy, self).__init__("http://conversioninsights.net/")

    def canonicalize(self, url):
        replaced = url.replace(self.rootUrl, "")
        if not replaced or replaced.endswith('/'):
            replaced += "index.html"
        return replaced

