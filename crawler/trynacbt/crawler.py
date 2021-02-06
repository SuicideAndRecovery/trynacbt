import re

from dateutil import parser
import scrapy
from scrapy.crawler import CrawlerProcess

import trynacbt.crawleduri as crawleduri
import trynacbt.thread as thread


def crawl_sitemap(url):
    '''Crawl a sitemap at URL url.'''
    crawleduri.initialize_data()
    thread.initialize_data()

    process = CrawlerProcess({
        'HTTPERROR_ALLOWED_CODES': [404]
    })
    _SitemapSpider.sitemap_urls = [url]
    process.crawl(_SitemapSpider)
    process.start()


class _SitemapSpider(scrapy.spiders.SitemapSpider):
    '''A spider to crawl the sitemap.'''
    name = 'trynacbt'
    allowed_domains = ['sanctioned-suicide.org']
    download_delay = 4

    def sitemap_filter(self, entries):
        for entry in entries:
            # entry example:
            # {
            #   'loc': 'https://suicideandrecovery.com/post-sitemap.xml',
            #   'lastmod': '2020-08-16T20:56:24+00:00'
            # }
            # The lastmod key may be missing.
            if not 'loc' in entry:
                continue

            uri = entry['loc']

            if (not uri.startswith('https://sanctioned-suicide.org/threads/')) and (
                    not uri.startswith('https://sanctioned-suicide.org/sitemap.xml')):
                continue

            datetimeModified = parser.parse(entry['lastmod']) \
                if 'lastmod' in entry \
                else None

            if datetimeModified is None \
                    or crawleduri.modified(uri, datetimeModified):
                yield entry

    def parse(self, response):
        _parse_thread(self, response)
        yield


def _parse_thread(self, response):
    '''Parse a thread, saving it to the database if nothing is missing.'''
    title = ''

    for titleResponse in response.css('h1.p-title-value'):
        title = titleResponse.get()
        # Strips out the excess spans and surrounding h1 tags.
        # Examples:
        # <h1 class="p-title-value"><span class="label label--accent" dir="auto">Venting</span><span class="label-append"> </span>I'm afraid of myself
        # </h1>
        # <h1 class="p-title-value">Idea?</h1>
        pattern = re.compile(r'<h1[^>]*?>(<span[^>]*>[^<]*</[^>]*>[^<]*<span[^>]*>[^<]*</[^>]*>)?([\s\S]*?)</h1>')
        match = pattern.match(title)
        if match:
            title = match.group(2).strip()
        break

    if title == '':
        print('Error: Missing title in ' + response.url)
        return

    print('-------' + title + '-------')

    isFirstPost = True
    posts = []

    for postResponse in response.css('article.message'):
        postIndex = None
        username = ''
        message = ''
        reactionCount = 0
        datetimePosted = None

        if isFirstPost:
            postIndex = 0
        else:
            for postIndexResponse in postResponse.css('article ::attr(id)'):
                postIndexWithExtraText = postIndexResponse.get()
                pattern = re.compile(r'js-post-(\d+)')
                match = pattern.match(postIndexWithExtraText)
                if match:
                    postIndex = match.group(1)
                break



        for usernameResponse in postResponse.css('.message-name span span ::text'):
            username = usernameResponse.get().strip()
            break

        if not username:
            for usernameResponse in postResponse.css('.message-name span ::text'):
                username = usernameResponse.get().strip()
                break

        for messageResponse in postResponse.css('article.message-body .bbWrapper'):
            message = messageResponse.get().strip()
            break

        for reactionResponse in postResponse.css('.reactionsBar .reactionsBar-link'):
            reactionText = reactionResponse.get()
            pattern = re.compile(r'.*?and (\d+) others')
            match = pattern.match(reactionText)
            if match:
                reactionCount = 3 + int(match.group(1))
            break

        for messageResponse in postResponse.css('time.u-dt ::attr(datetime)'):
            datetimePosted = parser.parse(messageResponse.get().strip())
            break

        print('--')
        print('postIndex: ' + str(postIndex))
        print('username: ' + username)
        print('message: ' + message)
        print('reactionCount: ' + str(reactionCount))
        print('date: ' + str(datetimePosted))

        isFirstPost = False

        if username == '' or message == '' \
                or datetimePosted is None or postIndex is None:
            print('Error: Missing username, message, date or index in ' + response.url)
            continue

        post = thread.Post(
            postIndex = postIndex,
            username = username,
            message = message,
            reactionCount = reactionCount,
            datetimePosted = datetimePosted
        )
        posts.append(post)

    thread.save(
        uri = response.url,
        title = title,
        posts = posts
    )
    crawleduri.save_crawled_now(response.url)


def crawl_page(url):
    '''Crawl a page at URL url.'''
    crawleduri.initialize_data()
    thread.initialize_data()

    process = CrawlerProcess({
        'HTTPERROR_ALLOWED_CODES': [404]
    })
    _PageSpider.start_urls = [url]
    process.crawl(_PageSpider)
    process.start()


class _PageSpider(scrapy.spiders.Spider):
    '''A spider to crawl a page.'''
    name = 'trynacbt'
    allowed_domains = ['sanctioned-suicide.org']
    download_delay = 4

    def parse(self, response):
        if response.url.startswith('https://sanctioned-suicide.org/threads/'):
            _parse_thread(self, response)
            yield
        else:
            for next_page in response.css('a'):
                next_anchor = next_page.get()
                if '/threads/' in next_anchor and not ('/page-' in next_anchor
                        ) and not ('/latest' in next_anchor):
                    yield response.follow(next_page, self.parse)
