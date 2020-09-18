from dateutil import parser
import sqlite3

import trynacbt.data.files as files


class Thread:
    '''Represents a thread on the forum.'''
    def __init__(self, uri, title, message):
        self.uri = uri
        self.title = title
        self.message = message


def initialize_data():
    '''Create the tables for storing crawled threads if needed.'''
    _ensure_tables_exist()


def _ensure_tables_exist():
    '''Ensure table(s) for storing crawled URIs exist.'''
    files.ensure_data_file_path()

    connection = sqlite3.connect(files.SQLITE_MAIN_PATH)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Threads(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            uri TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Posts(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            threadId INTEGER NOT NULL,
            postIndex INTEGER NOT NULL,
            message TEXT NOT NULL,
            reactionCount INTEGER NOT NULL,
            FOREIGN KEY(threadId) REFERENCES Threads(id),
            UNIQUE(threadId, postIndex)
        );
    ''')

    try:
        cursor.execute('ALTER TABLE Posts ADD COLUMN datetimePosted TEXT')
    except sqlite3.OperationalError as exception:
        if not 'duplicate column name' in str(exception):
            raise

    try:
        cursor.execute('ALTER TABLE Posts ADD COLUMN username TEXT')
    except sqlite3.OperationalError as exception:
        if not 'duplicate column name' in str(exception):
            raise

    connection.commit()
    connection.close()


def save(self, uri, username, title, message, reactionCount, datetimePosted):
    '''Save a crawled thread to the database.'''
    connection = sqlite3.connect(files.SQLITE_MAIN_PATH)
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO Threads
            (uri, title)
            VALUES (?, ?)
            ON CONFLICT (uri)
            DO UPDATE SET title = excluded.title;
    ''', (uri, title))

    cursor.execute('''
        INSERT INTO Posts
            (threadId, postIndex, message, reactionCount, datetimePosted,
                username)
            VALUES (?, 0, ?, ?, ?, ?)
            ON CONFLICT (threadId, postIndex)
            DO UPDATE SET message = excluded.message,
                reactionCount = excluded.reactionCount,
                datetimePosted = excluded.datetimePosted,
                username = excluded.username;
    ''', (cursor.lastrowid, message, reactionCount, \
            datetimePosted.isoformat(), username))

    connection.commit()
    connection.close()
