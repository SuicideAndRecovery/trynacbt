from trynacbtcrawler.data.ThreadDao import ThreadDao

class ThreadService(object):
    def __init__(self):
        '''Constructor.'''
        self._threadDao = ThreadDao()

    def initialize_data(self):
        '''Create the tables for storing crawled threads if needed.'''
        self._threadDao.ensure_tables_exist()

    def save(self, uri, username, title, message, reactionCount):
        '''Save a crawled thread.'''
        self._threadDao.save(
            uri=uri,
            username=username,
            title=title,
            message=message,
            reactionCount=reactionCount
        )
