#file to run multiple experiments in parallel and save to test.db (local file store sqlite)
#using SVMs for classification

import sqlite3
from sklearn.datasets import load_iris  # replace with your data loader
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from joblib import Parallel, delayed
import itertools
import uuid
import time
from filelock import FileLock
import os

# Function to run one experiment
def run_trial(C, kernel, gamma, X_train, X_test, y_train, y_test, exp_id):
    # Train
    clf = SVC(C=C, kernel=kernel, gamma=gamma)
    clf.fit(X_train, y_train)
    # Predict & metrics
    y_pred = clf.predict(X_test)
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted'),
        'recall': recall_score(y_test, y_pred, average='weighted'),
        'f1': f1_score(y_test, y_pred, average='weighted')
    }
    #file base lock
    lock_path = os.path.abspath("test.db.lock")
    with FileLock(lock_path):
        # Insert into DB
        conn = sqlite3.connect('test.db')
        cur = conn.cursor()
        # Insert Trial
        trial_id = str(uuid.uuid4())
        cur.execute("INSERT INTO Trial (Trial_ID, Experiment_ID, Status, StartTime, EndTime, Seed) VALUES (?, ?, ?, ?, ?, ?)", (trial_id, exp_id, 'completed', time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S'), 42))
        # Insert Hyperparameters
        hp_id = str(uuid.uuid4())
        cur.execute("INSERT INTO Hyperparameter (Hyperparameter_ID, Trial_ID, type, epochs, value) VALUES (?, ?, ?, ?, ?)",
                    (hp_id, trial_id, 'C', '0', C))
        hp_id = str(uuid.uuid4())
        cur.execute("INSERT INTO Hyperparameter (Hyperparameter_ID, Trial_ID, type, epochs, value) VALUES (?, ?, ?, ?, ?)",
                    (hp_id, trial_id, 'kernel', '0', kernel))
        hp_id = str(uuid.uuid4())
        cur.execute("INSERT INTO Hyperparameter (Hyperparameter_ID, Trial_ID, type, epochs, value) VALUES (?, ?, ?, ?, ?)",
                    (hp_id, trial_id, 'gamma', '0', gamma))
        # Insert Metrics
        for metric_name, metric_val in metrics.items():
            metric_id = str(uuid.uuid4())
            cur.execute("INSERT INTO Metric (Metric_ID, Trial_ID, name, value, TimeStamp) VALUES (?, ?, ?, ?, ?)",
                        (metric_id, trial_id, metric_name, float(metric_val), time.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
    return exp_id, metrics

def __main__():
    startTime = time.time()
    #create experiment id
    exp_id = str(uuid.uuid4())
    #create connection to db
    conn = sqlite3.connect('test.db')
    #create cursor
    cur = conn.cursor()
    # Parameters
    param_grid = {
        'C': [0.1, 1, 10, 100],
        'kernel': ['linear', 'rbf', 'poly', 'sigmoid'],
        'gamma': ['scale', 'auto', 0.01, 0.1]
    }

    # Prepare combinations
    combinations = list(itertools.product(param_grid['C'], param_grid['kernel'], param_grid['gamma']))

    # Load and split data
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    #Insert dataset
    dataset_id = str(uuid.uuid4())
    cur.execute("INSERT INTO Dataset (Dataset_ID, name, version, description, storage_location, size) VALUES (?, ?, ?, ?, ?, ?)", (dataset_id, 'Iris', '1.0', 'Iris dataset for classification', '/mnt/data/iris.csv', 150))

    # Insert Model
    model_id = str(uuid.uuid4())
    cur.execute("INSERT INTO Model (Model_ID, Name, Type, Version, Hyperparameters, ArtifactLocation) VALUES (?, ?, ?, ?, ?, ?)",
                (model_id, 'SVC', 'SVM', '1.0', 'C, kernel, gamma', '/mnt/data/model.pkl'))
    
    #close connection
    conn.commit()
    conn.close()
    
    #run trials in parallel
    results = Parallel(n_jobs=4)(delayed(run_trial)(C, kernel, gamma, X_train, X_test, y_train, y_test, exp_id) for C, kernel, gamma in combinations)
    endTime = time.time()

    #create connection to db
    conn = sqlite3.connect('test.db')
    #create cursor
    cur = conn.cursor()

    # Insert Experiment
    cur.execute("INSERT INTO Experiment (Experiment_ID, Name, Author_ID, Description, StartTimeStamp, EndTimeStamp, status, model_id, dataset_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (exp_id, 'Lyssa', 'Iris SVM Experiment', 'Experiment with SVM on Iris dataset', startTime, endTime, 'completed', model_id, dataset_id))
    
    print("Completed experiments:", results)
    #close connection
    conn.commit()
    conn.close()
    print("All trials completed in", endTime - startTime, "seconds")

#run main
if __name__ == "__main__":
    __main__()