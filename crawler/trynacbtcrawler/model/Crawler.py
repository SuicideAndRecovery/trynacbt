import re

from dateutil import parser
import scrapy
from scrapy.crawler import CrawlerProcess

from trynacbtcrawler.service.CrawledUriService import CrawledUriService
from trynacbtcrawler.service.ThreadService import ThreadService


class Crawler(object):
    '''A simple crawler for SanctionedSuicide threads.'''
    def crawl_sitemap(self, url):
        '''Crawl a sitemap at URL url.'''
        CrawledUriService().initialize_data()
        ThreadService().initialize_data()

        process = CrawlerProcess({
            'HTTPERROR_ALLOWED_CODES': [404]
        })
        _SitemapSpider.sitemap_urls = [url]
        process.crawl(_SitemapSpider)
        process.start()


class _SitemapSpider(scrapy.spiders.SitemapSpider):
    '''A spider to crawl the sitemap.'''
    name = 'TrynacbtCrawler'
    allowed_domains = ['sanctionedsuicide.com']
    download_delay = 4

    def sitemap_filter(self, entries):
        crawledUriService = CrawledUriService()

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
                    or crawledUriService.modified(uri, datetimeModified):
                yield entry

    def parse(self, response):
        crawledUriService = CrawledUriService()

        title = ''
        username = ''
        message = ''
        reactionCount = 0
        datetimePosted = None

        for titleResponse in response.css('h1.p-title-value ::text'):
            title = titleResponse.get()
            break

        for usernameResponse in response.css('.message-name span span ::text'):
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

        if title == '' or username == '' or message == '' or datetimePosted is None:
            return

        print(title)
        print(username)
        print(message)
        print(reactionCount)
        print(datetimePosted)

        ThreadService().save(
            uri=response.url,
            username=username,
            title=title,
            message=message,
            reactionCount=reactionCount,
            datetimePosted=datetimePosted
        )
        crawledUriService.save_crawled_now(response.url)

        yield
