import datetime

from trynacbt.data.CrawledUriDao import CrawledUriDao


class CrawledUriService(object):
    '''Service to query and record data about crawled URIs.'''

    def __init__(self):
        '''Constructor.'''
        self._crawledUriDao = CrawledUriDao()

    def initialize_data(self):
        '''Create the tables for storing crawled URIs if needed.'''
        self._crawledUriDao.ensure_tables_exist()

    def modified(self, uri, datetimeModified):
        '''Return true if the uri has been modified since last crawl.'''
        lastCrawled = self._crawledUriDao.crawled_datetime(uri)

        if lastCrawled is None:
            return True

        return lastCrawled < datetimeModified

    def save_crawled_now(self, uri):
        '''Save a crawled URI as being crawled at the current datetime.'''
        datetimeNow = datetime.datetime.now(datetime.timezone.utc)
        self._crawledUriDao.save(uri, datetimeNow)
