#!/usr/local/bin/python3
import argparse
import errno
import os
from Crawler import Crawler
from TestScrapingPolicy import TestScrapingPolicy

def main():
    argparser = argparse.ArgumentParser(description="Scrapes a Web site and writes the generated HTML to disk for caching")
    args = argparser.parse_args()

    policy = TestScrapingPolicy()
    try:
        os.makedirs(policy.getOutDirectory())
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    Crawler(policy).crawl()







main()
