from trynacbt.model.Crawler import Crawler


class CrawlController(object):
    '''Arranges the crawling of a website.'''

    def crawl_sitemap(self, url):
        '''Crawls a website's sitemap at URL url.'''
        crawler = Crawler()
        crawler.crawl_sitemap(url)
