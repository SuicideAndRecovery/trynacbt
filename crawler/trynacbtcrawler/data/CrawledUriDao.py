import sqlite3

from dateutil import parser

import trynacbtcrawler.data.files as files


class CrawledUriDao:
    def ensure_tables_exist(self):
        '''Ensure table(s) for storing crawled URIs exist.'''
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

    def crawled_datetime(self, uri):
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

    def save(self, uri, datetimeCrawled):
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
