'''
trynacbt crawler's command line

License:
    Copyright (c) 2020 SuicideAndRecovery
    This code is licensed to you under an open source license (MIT/X11).
    See the LICENSE file for details.
'''

import click
import scrapy

from trynacbt.model.Crawler import Crawler
import trynacbt.training as training


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
    Crawler().crawl_sitemap(url)

@main.command()
def trainset():
    '''
    Enter an interactive mode to modify the set of training data from the crawler.
    '''
    training.initialize_data()

    inputResponse = True
    thread = True

    while thread and inputResponse:
        thread = training.get_next_thread()
        if not thread:
            print('No threads left to classify.')
            continue

        print('---%s---' % thread.title)
        print('Message: %s' % thread.message)
        print('---')
        print('Would you want to be notified of this thread? (Nothing to quit)')

        inputResponse = input('(1) yes or (2) no or nothing: ')
        if inputResponse in ('1', '2'):
            training.save(thread, inputResponse == '1')


if __name__ == '__main__':
    main()
