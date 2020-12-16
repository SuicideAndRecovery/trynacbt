'''
trynacbt crawler's command line

License:
    Copyright (c) 2020 SuicideAndRecovery
    This code is licensed to you under an open source license (MIT/X11).
    See the LICENSE file for details.
'''

import click
import scrapy

import trynacbt.classifier as classifier
import trynacbt.crawler as crawler
import trynacbt.plugin as plugin
import trynacbt.trainingdata as trainingdata


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
    crawler.crawl_sitemap(url)


@main.command()
@click.argument('url')
def page(url):
    '''
    Crawls a page looking for SanctionedSuicide threads.
    '''
    crawler.crawl_page(url)


@main.command()
def trainset():
    '''
    Enter an interactive mode to modify the set of training data from the crawler.
    '''
    trainingdata.initialize_data()

    inputResponse = True
    thread = True

    while thread and inputResponse:
        thread = trainingdata.get_next_thread()
        if not thread:
            print('No threads left to classify.')
            continue

        print('---%s---' % thread.title)
        print('Message: %s' % thread.message)
        print('---')
        print('Would you want to be notified of this thread? (Nothing to quit)')

        inputResponse = input('(1) yes or (2) no or nothing: ')
        if inputResponse in ('1', '2'):
            trainingdata.save(thread, inputResponse == '1')


@main.command()
def learn():
    '''Learn (train the classifier) from the current set of training data.'''
    classifier.train()


@main.command()
def list():
    '''List recently found goodbye threads.'''
    goodbye_threads = classifier.recent_goodbye_threads()

    print('___Recent goodbye threads___:')

    for thread in goodbye_threads:
        print('---%s---' % thread.title)
        print('Message: %s' % thread.message)
        print('---')

@main.command()
@click.argument('url')
@click.argument('apikey')
def sync(url, apikey):
    '''Synchronize recent goodbye threads with a server running the plugin.'''
    goodbye_threads = classifier.recent_goodbye_threads()

    print('Attempting to sync with server.')

    plugin.sync_threads(url, apikey, goodbye_threads)


if __name__ == '__main__':
    main()
