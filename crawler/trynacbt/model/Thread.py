class Thread(object):
    '''Represents a thread on the forum.'''
    def __init__(self, uri, title, message):
        self.uri = uri
        self.title = title
        self.message = message
