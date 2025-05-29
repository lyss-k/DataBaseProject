import sqlite3
from sklearn.datasets import fetch_openml
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

# Load and preprocess data
def load_data():
    X, y = fetch_openml('Fashion-MNIST', version=1, return_X_y=True, as_frame=False)
    X = X / 255.0  # Normalize pixel values to [0, 1]
    return train_test_split(X, y, test_size=0.2, random_state=42)

# Function to run one experiment trial
def run_trial(hidden_layer_sizes, activation, learning_rate_init, X_train, X_test, y_train, y_test, exp_id):
    clf = MLPClassifier(hidden_layer_sizes=hidden_layer_sizes,
                        activation=activation,
                        learning_rate_init=learning_rate_init,
                        max_iter=30,  # Longer = slower
                        early_stopping=True,
                        random_state=42)

    clf.fit(X_train, y_train)

    # Predict and calculate metrics
    y_pred = clf.predict(X_test)
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
        'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
        'f1': f1_score(y_test, y_pred, average='weighted', zero_division=0)
    }

    # Lock to safely write to DB
    lock_path = os.path.abspath(SQLITE_FILE_PATH + ".lock")
    with FileLock(lock_path):
        conn = sqlite3.connect(SQLITE_FILE_PATH)
        cur = conn.cursor()

        trial_id = str(uuid.uuid4())
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        # Trial
        cur.execute("INSERT INTO Trial (Trial_ID, Experiment_ID, Status, StartTime, EndTime, Seed) VALUES (?, ?, ?, ?, ?, ?)",
                    (trial_id, exp_id, 'completed', now, now, 42))

        # Hyperparameters
        for param_name, param_val in {
            'hidden_layer_sizes': str(hidden_layer_sizes),
            'activation': activation,
            'learning_rate_init': learning_rate_init
        }.items():
            hp_id = str(uuid.uuid4())
            cur.execute("INSERT INTO Hyperparameter (Hyperparameter_ID, Trial_ID, type, epochs, value) VALUES (?, ?, ?, ?, ?)",
                        (hp_id, trial_id, param_name, '0', param_val))

        # Metrics
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

    # Experiment parameters
    param_grid = {
        'hidden_layer_sizes': [(128, 64), (256, 128), (256, 128, 64)],
        'activation': ['relu', 'tanh'],
        'learning_rate_init': [0.001, 0.005]
    }

    combinations = list(itertools.product(
        param_grid['hidden_layer_sizes'],
        param_grid['activation'],
        param_grid['learning_rate_init']
    ))

    # Load and split data
    X_train, X_test, y_train, y_test = load_data()

    # Insert dataset record
    dataset_id = str(uuid.uuid4())
    cur.execute("INSERT INTO Dataset (Dataset_ID, name, version, description, storage_location, size) VALUES (?, ?, ?, ?, ?, ?)",
                (dataset_id, 'Fashion-MNIST', '1.0', 'Image classification dataset', '/mnt/data/fmnist.csv', 70000))

    # Insert model record
    model_id = str(uuid.uuid4())
    cur.execute("INSERT INTO Model (Model_ID, Name, Type, Version, Hyperparameters, ArtifactLocation) VALUES (?, ?, ?, ?, ?, ?)",
                (model_id, 'MLPClassifier', 'NeuralNet', '1.0',
                 'hidden_layer_sizes, activation, learning_rate_init',
                 '/mnt/data/mlp_model.pkl'))

    conn.commit()
    conn.close()

    # Run trials in parallel
    results = Parallel(n_jobs=4)(
        delayed(run_trial)(hls, act, lr, X_train, X_test, y_train, y_test, exp_id)
        for hls, act, lr in combinations
    )

    endTime = datetime.now()

    # Finalize experiment entry
    conn = sqlite3.connect(SQLITE_FILE_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO Experiment (Experiment_ID, Name, Author_ID, Description, StartTimeStamp, EndTimeStamp, status, model_id, dataset_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (exp_id, 'FashionNN', 'lyssa', 'Fashion-MNIST NN experiments',
                 startTime.strftime('%Y-%m-%d %H:%M:%S'),
                 endTime.strftime('%Y-%m-%d %H:%M:%S'),
                 'completed', model_id, dataset_id))

    conn.commit()
    conn.close()

    print("Completed experiments:", results)
    print("All trials completed in", endTime - startTime, "seconds")

# Run the main function
if __name__ == "__main__":
    __main__()
