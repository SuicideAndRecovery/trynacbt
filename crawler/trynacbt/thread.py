from dateutil import parser
import sqlite3

import trynacbt.files as files


class Thread:
    '''Represents a thread on the forum.'''
    def __init__(self, uri, title, message, datetimePosted):
        self.uri = uri
        self.title = title
        self.message = message
        self.datetimePosted = datetimePosted


class Post:
    '''Represents a single post in a thread on the forum.'''
    def __init__(self, postIndex, username, message, reactionCount, datetimePosted):
        self.postIndex = postIndex
        self.username = username
        self.message = message
        self.reactionCount = reactionCount
        self.datetimePosted = datetimePosted


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


def save(uri, title, posts):
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

    connection.commit()

    # Get the ID of the thread.
    cursor.execute('''
        SELECT id
            FROM Threads
            WHERE uri = ?;
    ''', (uri,))
    row = cursor.fetchone()
    if row:
        threadId = row[0]

    for post in posts:
        cursor.execute('''
            INSERT INTO Posts
                (threadId, postIndex, message, reactionCount, datetimePosted,
                    username)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (threadId, postIndex)
                DO UPDATE SET message = excluded.message,
                    reactionCount = excluded.reactionCount,
                    datetimePosted = excluded.datetimePosted,
                    username = excluded.username;
        ''', (threadId, post.postIndex, post.message, post.reactionCount, \
                post.datetimePosted.isoformat(), post.username))

    connection.commit()
    connection.close()
