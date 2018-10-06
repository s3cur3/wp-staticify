#!/usr/local/bin/python3
import argparse
from Crawler import Crawler
from ScrapingPolicy import ScrapingPolicy

def main():
    argparser = argparse.ArgumentParser(description="Scrapes a Web site and writes the generated HTML to disk for caching")
    argparser.add_argument('root', help='The starting point URL for the crawl (beginning with http:// or https://)')
    args = argparser.parse_args()

    assert args.root.startswith(('https://', 'http://'))
    policy = ScrapingPolicy(args.root)
    Crawler(policy).crawl()


main()
