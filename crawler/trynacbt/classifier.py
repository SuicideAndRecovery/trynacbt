import datetime
import sqlite3

import tensorflow
import tensorflow_hub

import trynacbt.trainingdata as trainingdata
import trynacbt.files as files
import trynacbt.thread as thread


def _get_dataset_size(dataset):
    '''Return the size of the dataset.'''
    size = 0

    for _ in dataset:
        size += 1

    return size


def _create_model():
    tensorflow_model = tensorflow.keras.Sequential()

    embedding = 'https://tfhub.dev/google/tf2-preview/gnews-swivel-20dim/1'
    hub_layer = tensorflow_hub.KerasLayer(
        embedding,
        input_shape=[],
        dtype=tensorflow.string,
        trainable=True
    )
    tensorflow_model.add(hub_layer)
    tensorflow_model.add(tensorflow.keras.layers.Dense(16, activation='relu'))
    tensorflow_model.add(tensorflow.keras.layers.Dense(1))

    tensorflow_model.compile(
        optimizer='adam',
        loss=tensorflow.losses.BinaryCrossentropy(from_logits=True),
        metrics=['accuracy']
    )

    return tensorflow_model


def _recent_threads():
    '''Return a tuple containing a TensorFlow DataSet with recent threads and
    a list of those recent threads as Thread objects.'''
    datetime_last_week = datetime.datetime.now(datetime.timezone.utc) - (
            datetime.timedelta(days=7))
    datetime_last_week_iso = datetime_last_week.isoformat()

    connection = sqlite3.connect(files.SQLITE_MAIN_PATH)
    cursor = connection.cursor()

    cursor.execute('''
        SELECT T.uri, T.title, P.message, P.datetimePosted
            FROM Threads T
            JOIN Posts P
                ON T.id = P.threadId
                    AND P.postIndex = 0
                    AND P.datetimePosted >= ?
            JOIN TrainingGoodbyeThreads TGT
                ON TGT.threadId = T.id
                    AND TGT.isGoodbyeThread = 1
            UNION
            SELECT T2.uri, T2.title, P2.message, P2.datetimePosted
                FROM Threads T2
                JOIN Posts P2
                    ON T2.id = P2.threadId
                        AND P2.postIndex = 0
                        AND P2.datetimePosted >= ?
                LEFT JOIN TrainingGoodbyeThreads TGT2
                    ON TGT2.threadId = T2.id
                WHERE TGT2.id IS NULL
                ORDER BY datetimePosted DESC;
    ''', (datetime_last_week_iso, datetime_last_week_iso))

    threads = []
    row = cursor.fetchone()
    while row:
        threads.append(thread.Thread(row[0], row[1], row[2]))
        row = cursor.fetchone()

    connection.close()

    threads_input = []
    for t in threads:
        threads_input.append('%s %s' % (t.title, t.message))

    return (
        tensorflow.constant(threads_input),
        threads
    )


def recent_goodbye_threads():
    tensorflow_model = _create_model()
    tensorflow_model.load_weights(files.GOODBYE_CLASSIFIER_PATH)

    threads_tuple =_recent_threads()
    threads_input_tensor = threads_tuple[0]
    all_threads = threads_tuple[1]

    goodbye_predictions = tensorflow_model.predict(threads_input_tensor)

    goodbye_threads = []
    for prediction, t in zip(goodbye_predictions, all_threads):
        if prediction > 0:
            print(prediction)
            goodbye_threads.append(t)

    return goodbye_threads


def train():
    '''Train the classifier on the training data.'''
    dataset = trainingdata.training_dataset()
    dataset_size = _get_dataset_size(dataset)

    training_size = int(0.7 * dataset_size)
    validation_size = int(0.15 * dataset_size)
    test_size = validation_size

    training_dataset = dataset.take(training_size)
    test_dataset = dataset.skip(training_size)
    validation_dataset = test_dataset.take(validation_size)
    test_dataset = test_dataset.skip(validation_size)

    tensorflow_model = _create_model()

    EPOCHS = 30
    training_batch_size = int(training_size / EPOCHS)
    validation_batch_size = int(validation_size / EPOCHS)

    history = tensorflow_model.fit(
        training_dataset.batch(training_batch_size),
        epochs=EPOCHS,
        validation_data = validation_dataset.batch(validation_batch_size),
        verbose=1
    )

    test_batch_size = int(test_size / EPOCHS)

    results = tensorflow_model.evaluate(test_dataset.batch(test_batch_size))
    for name, value in zip(tensorflow_model.metrics_names, results):
        print('%s: %.3f' % (name, value))

    tensorflow_model.save_weights(files.GOODBYE_CLASSIFIER_PATH)
