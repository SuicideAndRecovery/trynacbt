import sqlite3

import trynacbt.files as files
import trynacbt.thread as thread


def initialize_data():
    '''Create the tables for storing the training data if needed.'''
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


def get_next_thread():
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

    return thread.Thread(row[0], row[1], row[2])


def save(thread, isGoodbyeThread):
    '''Record a thread as a goodbye or non-goodbye thread in the training data.'''
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
