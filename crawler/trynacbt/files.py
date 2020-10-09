import os

import appdirs


_AUTHOR = 'SuicideAndRecovery'
_APPLICATION_NAME = 'trynacbt'


def data_file_path(filename):
    '''Return the path to a file in the data directory.'''
    return os.path.join(
        appdirs.user_data_dir(_AUTHOR, _APPLICATION_NAME),
        filename
    )


def ensure_data_file_path():
    '''Ensure the path to the data directory exists.'''
    os.makedirs(data_file_path(''), exist_ok=True)


GOODBYE_CLASSIFIER_PATH = data_file_path('goodbye_classifier')


SQLITE_MAIN_PATH = data_file_path('trynacbt_main.sqlite')
