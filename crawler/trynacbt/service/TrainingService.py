from trynacbt.model.Thread import Thread
from trynacbt.data.TrainingDao import TrainingDao

class TrainingService(object):
    def __init__(self):
        '''Constructor.'''
        self._trainingDao = TrainingDao()

    def initialize_data(self):
        '''Create the tables for storing the training data if needed.'''
        self._trainingDao.ensure_tables_exist()

    def get_next_thread(self):
        '''Get the next thread to classify for training data.'''
        return self._trainingDao.get_next_thread()

    def save(self, thread, isGoodbyeThread):
        '''Record a thread as a goodbye or non-goodbye thread in the training data.'''
        self._trainingDao.save(thread, isGoodbyeThread)
