import sqlite3

import trynacbt.data.files as files
from trynacbt.model.Thread import Thread


class TrainingDao:
    def ensure_tables_exist(self):
        '''Ensure table(s) for storing training data exist.'''
        files.ensure_data_file_path()

        connection = sqlite3.connect(files.SQLITE_MAIN_PATH)
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS TrainingGoodbyeThreads(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                threadId INTEGER NOT NULL,
                isGoodbyeThread INTEGER NOT NULL,
                FOREIGN KEY(threadId) REFERENCES Threads(id),
                UNIQUE(threadId)
            );
        ''')

        connection.commit()
        connection.close()

    def get_next_thread(self):
        '''Return the next thread to classify or None if no threads left.'''
        connection = sqlite3.connect(files.SQLITE_MAIN_PATH)
        cursor = connection.cursor()

        cursor.execute('''
            SELECT T.uri, T.title, P.message
                FROM Threads T
                JOIN Posts P
                    ON T.id = P.threadId
                        AND P.postIndex = 0
                LEFT JOIN TrainingGoodbyeThreads TGT
                    ON TGT.threadId = T.id
                WHERE TGT.id IS NULL
                ORDER BY RANDOM()
                LIMIT 1;
        ''')

        row = cursor.fetchone()

        connection.close()

        if not row:
            return None

        return Thread(row[0], row[1], row[2])

    def save(self, thread, isGoodbyeThread):
        '''Save a thread to the database as a goodbye thread or not.'''
        connection = sqlite3.connect(files.SQLITE_MAIN_PATH)
        cursor = connection.cursor()

        cursor.execute('''
            SELECT id
                FROM Threads
                WHERE uri = ?;
        ''', (thread.uri,))

        row = cursor.fetchone()

        cursor.execute('''
            INSERT INTO TrainingGoodbyeThreads
                (threadId, isGoodbyeThread)
                VALUES (?, ?)
                ON CONFLICT (threadId)
                DO UPDATE SET isGoodbyeThread = excluded.isGoodbyeThread;
        ''', (row[0], isGoodbyeThread))

        connection.commit()
        connection.close()
