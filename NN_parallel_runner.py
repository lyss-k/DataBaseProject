import sqlite3
from sklearn.datasets import load_iris
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from joblib import Parallel, delayed
import itertools
import uuid
import time
from filelock import FileLock
import os
from datetime import datetime

SQLITE_FILE_PATH = "MLED_transactions.db"

# Function to run one experiment
def run_trial(hidden_layer_sizes, activation, learning_rate_init, X_train, X_test, y_train, y_test, exp_id):
    # Train
    clf = MLPClassifier(hidden_layer_sizes=hidden_layer_sizes,
                        activation=activation,
                        learning_rate_init=learning_rate_init,
                        max_iter=300,
                        random_state=42)
    clf.fit(X_train, y_train)

    # Predict & metrics
    y_pred = clf.predict(X_test)
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted'),
        'recall': recall_score(y_test, y_pred, average='weighted'),
        'f1': f1_score(y_test, y_pred, average='weighted')
    }

    # Lock DB writes
    lock_path = os.path.abspath(SQLITE_FILE_PATH + ".lock")
    with FileLock(lock_path):
        conn = sqlite3.connect(SQLITE_FILE_PATH)
        cur = conn.cursor()

        # Insert Trial
        trial_id = str(uuid.uuid4())
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("INSERT INTO Trial (Trial_ID, Experiment_ID, Status, StartTime, EndTime, Seed) VALUES (?, ?, ?, ?, ?, ?)",
                    (trial_id, exp_id, 'completed', now, now, 42))

        # Insert Hyperparameters
        for param_name, param_val in {
            'hidden_layer_sizes': str(hidden_layer_sizes),
            'activation': activation,
            'learning_rate_init': learning_rate_init
        }.items():
            hp_id = str(uuid.uuid4())
            cur.execute("INSERT INTO Hyperparameter (Hyperparameter_ID, Trial_ID, type, epochs, value) VALUES (?, ?, ?, ?, ?)",
                        (hp_id, trial_id, param_name, '0', param_val))

        # Insert Metrics
        for metric_name, metric_val in metrics.items():
            metric_id = str(uuid.uuid4())
            cur.execute("INSERT INTO Metric (Metric_ID, Trial_ID, name, value, TimeStamp) VALUES (?, ?, ?, ?, ?)",
                        (metric_id, trial_id, metric_name, float(metric_val), now))

        conn.commit()
        conn.close()

    return exp_id, metrics

def __main__():
    startTime = datetime.now()
    exp_id = str(uuid.uuid4())

    conn = sqlite3.connect(SQLITE_FILE_PATH)
    cur = conn.cursor()

    # Parameters
    param_grid = {
        'hidden_layer_sizes': [(10,), (50,), (50, 20)],
        'activation': ['relu', 'tanh'],
        'learning_rate_init': [0.001, 0.01]
    }

    combinations = list(itertools.product(
        param_grid['hidden_layer_sizes'],
        param_grid['activation'],
        param_grid['learning_rate_init']
    ))

    # Load and split data
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Insert dataset
    dataset_id = str(uuid.uuid4())
    cur.execute("INSERT INTO Dataset (Dataset_ID, name, version, description, storage_location, size) VALUES (?, ?, ?, ?, ?, ?)",
                (dataset_id, 'Iris', '1.0', 'Iris dataset for classification', '/mnt/data/iris.csv', 150))

    # Insert model
    model_id = str(uuid.uuid4())
    cur.execute("INSERT INTO Model (Model_ID, Name, Type, Version, Hyperparameters, ArtifactLocation) VALUES (?, ?, ?, ?, ?, ?)",
                (model_id, 'MLPClassifier', 'NeuralNet', '1.0', 'hidden_layer_sizes, activation, learning_rate_init', '/mnt/data/mlp_model.pkl'))

    conn.commit()
    conn.close()

    # Run in parallel
    results = Parallel(n_jobs=4)(
        delayed(run_trial)(hls, act, lr, X_train, X_test, y_train, y_test, exp_id)
        for hls, act, lr in combinations
    )

    endTime = datetime.now()

    # Insert experiment
    conn = sqlite3.connect(SQLITE_FILE_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO Experiment (Experiment_ID, Name, Author_ID, Description, StartTimeStamp, EndTimeStamp, status, model_id, dataset_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (exp_id, 'Iris NN Experiment', 'Lyssa', 'Neural net on Iris dataset', startTime.strftime('%Y-%m-%d %H:%M:%S'), endTime.strftime('%Y-%m-%d %H:%M:%S'), 'completed', model_id, dataset_id))

    conn.commit()
    conn.close()

    print("Completed experiments:", results)
    print("All trials completed in", endTime - startTime, "seconds")

# Run
if __name__ == "__main__":
    __main__()
