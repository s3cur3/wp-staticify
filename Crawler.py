import errno
import os
from bs4 import BeautifulSoup
from functools import partial
from ScrapingPolicy import ScrapingPolicy  # for the sake of PyCharm's auto-documentation
from tornado import ioloop
from tornado.httpclient import AsyncHTTPClient, HTTPError
from urllib.parse import urlparse

class Crawler:
    def __init__(self, policy):
        """
        :type policy: ScrapingPolicy
        """
        self.policy = policy
        self.requests_in_flight = 0
        self.crawled = set()
        self.backlog = set()
        self.redirects = {}  # maps URLs to their destination
        self.errors = {}  # maps URLs to their (error) HTTP status codes
        AsyncHTTPClient.configure(None, defaults=dict(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'))
        self.http_client = AsyncHTTPClient(max_clients=policy.max_concurrent_requests)

    def crawl(self):
        """
        Crawls the site and writes the scraped HTML (and images, etc.) to disk
        """
        self.enqueue_urls([self.policy.start_at_url])
        ioloop.IOLoop.instance().start()

        # Only after IOLoop.instance().stop() has been called...
        with open(os.path.join(self.policy.out_directory, 'errors.log'), 'w') as error_file:
            error_file.writelines(f"HTTP Status {status_code}: {url}\n" for url, status_code in self.errors.items())

        with open(os.path.join(self.policy.out_directory, 'redirects.conf'), 'w') as redirects_file:
            for original, destination in self.redirects.items():
                parsed = urlparse(original)
                if parsed.query:
                    # TODO: This really needs a test on a live Nginx server!
                    redirects_file.write(
                        f"if ($args ~* \"{parsed.query}\") {{"
                        f"    rewrite ^{destination}? last;"
                        "}\n")
                else:
                    redirects_file.write(f"rewrite ^{parsed.path}$ {destination} permanent;\n")


    def handle_response(self, url, response):
        def find_links(html, policy):
            """
            :type html: str
            :type policy: ScrapingPolicy
            :rtype: Iterator[str]
            """
            soup = BeautifulSoup(html, 'lxml')
            for element in soup.find_all():
                if 'srcset' in element.attrs:
                    for source in element.attrs['srcset'].split(','):
                        src = source.rsplit(' ', 1)[:-1]
                        if policy.shouldCrawlUrl(src):
                            yield policy.canonicalize(src)
                else:
                    for potential_attr in ['href', 'src']:
                        if potential_attr in element.attrs and policy.shouldCrawlUrl(element.attrs[potential_attr]):
                            yield policy.canonicalize(element.attrs[potential_attr])


        if response.error:
            try:
                self.errors[url] = response.error.code
            except:
                self.errors[url] = str(response.error)
        else:
            if self.response_is_text(response):
                content = response.body.decode('utf-8')
                linked_urls = find_links(content, self.policy)
                self.enqueue_urls(linked_urls)
            else:  # treat as binary
                content = response.body
            self.scrape(url, response.effective_url, content)

        self.requests_in_flight -= 1

        self.run_backlog()

    @staticmethod
    def response_is_text(response):
        """
        :type response: httpclient.HTTPResponse
        :rtype: bool
        """
        if 'content-type' in response.headers:
            return not response.headers['content-type'] or response.headers['content-type'].startswith('text/')
        return False

    def enqueue_urls(self, urls):
        """
        :type urls: Iterable[str]
        """
        for url in urls:
            if url not in self.crawled:
                if self.requests_in_flight < self.policy.max_concurrent_requests:
                    self._enqueue_internal(url)
                else:
                    self.backlog.add(url)

    def _enqueue_internal(self, url):
        self.crawled.add(url)
        self.requests_in_flight += 1
        self.http_client.fetch(url.strip(), partial(self.handle_response, url), raise_error=False)

    def run_backlog(self):
        while self.backlog and self.requests_in_flight < self.policy.max_concurrent_requests:
            self._enqueue_internal(self.backlog.pop())

        if not self.backlog and self.requests_in_flight == 0:
            ioloop.IOLoop.instance().stop()  # all done!!

    def scrape(self, initial_url, final_url, content):
        """
        :param initial_url: The URL you requested
        :type initial_url: str
        :param final_url: The URL you wound up at after any redirects (may be the same!)
        :type final_url: str
        :param content: The full content of the URL; may be HTML for us to parse, or just binary data; in either case it gets written to disk
        :type content: str|bytes
        """
        assert content

        if initial_url != final_url:
            self.redirects[initial_url] = final_url

        if self.policy.shouldScrapeUrl(final_url):
            path = self.get_local_path_from_url(final_url)
            try:  # Create the parent directory
                os.makedirs(os.path.abspath(os.path.join(path, os.pardir)))
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise exception
            if isinstance(content, str):
                with open(path, 'w') as f:
                    f.write(self.policy.extractContent(content))
            else:
                with open(path, 'wb') as f:
                    f.write(content)

    def get_local_path_from_url(self, canonical_url):
        """
        :type canonical_url: str
        :return: str
        """
        url_path = urlparse(canonical_url).path  # ignore the domain
        assert url_path.startswith('/')
        if url_path.endswith('/'):
            url_path += 'index.html'
        elif '.' not in url_path.split('/')[-1]:  # no extension in the final path component
            url_path += '/index.html'
        return os.path.join(self.policy.out_directory, url_path[1:])  # drop the leading slash


