'''
trynacbt crawler's command line

License:
    Copyright (c) 2020 SuicideAndRecovery
    This code is licensed to you under an open source license (MIT/X11).
    See the LICENSE file for details.
'''

import click
import scrapy

from trynacbt.controller.CrawlController import CrawlController


@click.group()
def main():
    '''
    trynacbt's crawler is a program to crawl a website.
    '''


@main.command()
@click.argument('url')
def sitemap(url):
    '''
    Crawls a sitemap.
    '''
    CrawlController().crawl_sitemap(url)


if __name__ == '__main__':
    main()
