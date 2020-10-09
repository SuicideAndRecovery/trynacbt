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
    allowed_domains = ['sanctionedsuicide.com']
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

            if (not uri.startswith('https://sanctionedsuicide.com/threads/')) and (
                    not uri.startswith('https://sanctionedsuicide.com/sitemap.xml')):
                continue

            datetimeModified = parser.parse(entry['lastmod']) \
                if 'lastmod' in entry \
                else None

            if datetimeModified is None \
                    or crawleduri.modified(uri, datetimeModified):
                yield entry

    def parse(self, response):
        title = ''
        username = ''
        message = ''
        reactionCount = 0
        datetimePosted = None

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
                title = match.group(2)
            break

        for usernameResponse in response.css('.message-name span span ::text'):
            username = usernameResponse.get()
            break

        if not username:
            for usernameResponse in response.css('.message-name span ::text'):
                username = usernameResponse.get()
                break

        for messageResponse in response.css('article.message-body .bbWrapper'):
            message = messageResponse.get()
            break

        for reactionResponse in response.css('.reactionsBar .reactionsBar-link'):
            reactionText = reactionResponse.get()
            pattern = re.compile(r'.*?and (\d+) others')
            match = pattern.match(reactionText)
            if match:
                reactionCount = 3 + int(match.group(1))
            break

        for messageResponse in response.css('time.u-dt ::attr(datetime)'):
            datetimePosted = parser.parse(messageResponse.get())
            break

        print(title)
        print(username)
        print(message)
        print(reactionCount)
        print(datetimePosted)

        if title == '' or username == '' or message == '' or datetimePosted is None:
            return

        thread.save(
            uri=response.url,
            username=username,
            title=title,
            message=message,
            reactionCount=reactionCount,
            datetimePosted=datetimePosted
        )
        crawleduri.save_crawled_now(response.url)

        yield
