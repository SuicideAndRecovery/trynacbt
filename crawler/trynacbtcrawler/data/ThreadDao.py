import sqlite3

from dateutil import parser

import trynacbtcrawler.data.files as files


class ThreadDao:
    def ensure_tables_exist(self):
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

        connection.commit()
        connection.close()

    def save(self, uri, username, title, message, reactionCount):
        '''Save a thread to the database.'''
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
                (threadId, postIndex, message, reactionCount)
                VALUES (?, 0, ?, ?)
                ON CONFLICT (threadId, postIndex)
                DO UPDATE SET postIndex = excluded.postIndex,
                    message = excluded.message;
        ''', (cursor.lastrowid, message, reactionCount))

        connection.commit()
        connection.close()
