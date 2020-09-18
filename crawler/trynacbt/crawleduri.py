import datetime
import sqlite3

from dateutil import parser

import trynacbt.files as files

'''Service to query and record data about crawled URIs.'''


def initialize_data():
    '''Create the tables for storing crawled URIs if needed.'''
    files.ensure_data_file_path()

    connection = sqlite3.connect(files.SQLITE_MAIN_PATH)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CrawledUris(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            uri TEXT UNIQUE NOT NULL,
            datetimeCrawled TEXT NOT NULL
        );
    ''')

    connection.commit()
    connection.close()


def _crawled_datetime(uri):
    '''Return None or a datetime the URI was last crawled.'''
    connection = sqlite3.connect(files.SQLITE_MAIN_PATH)
    cursor = connection.cursor()

    cursor.execute('''
        SELECT datetimeCrawled
            FROM CrawledUris
            WHERE uri = ?;
    ''', (uri,))

    row = cursor.fetchone()
    datetimeCrawled = None
    if row:
        datetimeCrawled = parser.parse(row[0])

    connection.close()

    return datetimeCrawled


def modified(uri, datetimeModified):
    '''Return true if the uri has been modified since last crawl.'''
    lastCrawled = _crawled_datetime(uri)

    if lastCrawled is None:
        return True

    return lastCrawled < datetimeModified


def save(uri, datetimeCrawled):
    '''Save the datetime crawled for the specified URI.'''
    connection = sqlite3.connect(files.SQLITE_MAIN_PATH)
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO CrawledUris
            (uri, datetimeCrawled)
            VALUES (?, ?)
            ON CONFLICT (uri)
            DO UPDATE SET datetimeCrawled = excluded.datetimeCrawled;
    ''', (uri, datetimeCrawled.isoformat()))

    connection.commit()
    connection.close()


def save_crawled_now(uri):
    '''Save a crawled URI as being crawled at the current datetime.'''
    datetimeNow = datetime.datetime.now(datetime.timezone.utc)
    save(uri, datetimeNow)
