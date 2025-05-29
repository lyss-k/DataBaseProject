import sqlite3
from datetime import datetime, timedelta
import uuid
import random

DATABASE = "MLED_transactions.db"

# Helper function to generate UUID
def generate_uuid():
    return str(uuid.uuid4())

# Helper function to generate a random timestamp
def random_timestamp(start_days=0, end_days=30):
    return (datetime.now() - timedelta(days=random.randint(start_days, end_days))).strftime('%Y-%m-%d %H:%M:%S')

# Function to insert fake data
def insert_fake_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Insert Users
    users = [
        (generate_uuid(), "Alice", "Johnson", "alice@example.com", "Data Scientist"),
        (generate_uuid(), "Bob", "Smith", "bob@example.com", "ML Engineer"),
        (generate_uuid(), "Charlie", "Brown", "charlie@example.com", "Researcher")
    ]
    cursor.executemany("INSERT INTO User (User_ID, First_Name, Last_Name, Email, Role) VALUES (?, ?, ?, ?, ?)", users)

    # Insert Datasets
    datasets = [
        (generate_uuid(), "Dataset_A", 1, "First dataset description", "/path/to/dataset_a", 500),
        (generate_uuid(), "Dataset_B", 1, "Second dataset description", "/path/to/dataset_b", 700),
        (generate_uuid(), "Dataset_C", 2, "Third dataset description", "/path/to/dataset_c", 1000)
    ]
    cursor.executemany("INSERT INTO Dataset (DataSet_ID, Name, Version, Description, Storage_Location, Size) VALUES (?, ?, ?, ?, ?, ?)", datasets)

    # Insert Models
    models = [
        (generate_uuid(), "Model_X", "Neural Network", 1, '{"learning_rate": 0.01, "batch_size": 32}', "/models/model_x"),
        (generate_uuid(), "Model_Y", "Decision Tree", 1, '{"max_depth": 10}', "/models/model_y"),
        (generate_uuid(), "Model_Z", "Regression", 2, '{"regularization": 0.1}', "/models/model_z")
    ]
    cursor.executemany("INSERT INTO Model (Model_ID, Name, Type, Version, Hyperparameters, ArtifactLocation) VALUES (?, ?, ?, ?, ?, ?)", models)

    # Fetch IDs for FK references
    cursor.execute("SELECT User_ID FROM User")
    user_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DataSet_ID FROM Dataset")
    dataset_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT Model_ID FROM Model")
    model_ids = [row[0] for row in cursor.fetchall()]

    # Insert Experiments
    experiments = []
    for _ in range(3):
        experiments.append((
            generate_uuid(),
            f"Experiment_{random.randint(1000, 9999)}",
            random.choice(user_ids),
            "Testing different model architectures",
            random_timestamp(10, 30),
            random_timestamp(0, 10),
            random.choice(["Running", "Completed", "Failed"]),
            random.choice(model_ids),
            random.choice(dataset_ids)
        ))
    cursor.executemany("INSERT INTO Experiment (Experiment_ID, Name, Author_ID, Description, StartTimeStamp, EndTimeStamp, Status, Model_ID, DataSet_ID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", experiments)

    # Fetch Experiment IDs
    cursor.execute("SELECT Experiment_ID FROM Experiment")
    experiment_ids = [row[0] for row in cursor.fetchall()]

    # Insert Trials
    trials = []
    for _ in range(4):
        trials.append((
            generate_uuid(),
            random.choice(experiment_ids),
            random.choice(["Running", "Completed", "Failed"]),
            random_timestamp(5, 15),
            random_timestamp(0, 5),
            random.randint(1, 100)
        ))
    cursor.executemany("INSERT INTO Trial (Trial_ID, Experiment_ID, Status, StartTime, EndTime, Seed) VALUES (?, ?, ?, ?, ?, ?)", trials)

    # Fetch Trial IDs
    cursor.execute("SELECT Trial_ID FROM Trial")
    trial_ids = [row[0] for row in cursor.fetchall()]

    # Insert Hyperparameters
    hyperparameters = []
    for _ in range(4):
        hyperparameters.append((
            generate_uuid(),
            random.choice(trial_ids),
            random.choice(["Learning Rate", "Batch Size", "Dropout Rate"]),
            random.randint(1, 50),
            random.randint(1, 100)
        ))
    cursor.executemany("INSERT INTO Hyperparameter (Hyperparameter_ID, Trial_ID, Type, Epochs, Value) VALUES (?, ?, ?, ?, ?)", hyperparameters)

    # Insert Metrics
    metrics = []
    for _ in range(4):
        metrics.append((
            generate_uuid(),
            random.choice(trial_ids),
            random.choice(["Accuracy", "Loss", "F1 Score"]),
            random.randint(50, 100),
            random_timestamp(0, 2)
        ))
    cursor.executemany("INSERT INTO Metric (Metric_ID, Trial_ID, Name, Value, TimeStamp) VALUES (?, ?, ?, ?, ?)", metrics)

    # Insert Error Logs
    error_logs = []
    for _ in range(3):
        error_logs.append((
            generate_uuid(),
            random.choice(experiment_ids),
            random.choice(trial_ids),
            random_timestamp(0, 5),
            "Runtime error occurred during training",
            "Stack trace: ValueError at line 23"
        ))
    cursor.executemany("INSERT INTO ErrorLog (Error_ID, Experiment_ID, Trial_ID, TimeStamp, ErrorMessage, ErrorDetails) VALUES (?, ?, ?, ?, ?, ?)", error_logs)

    conn.commit()
    conn.close()

    print("Fake data inserted successfully.")

# Run the script
if __name__ == "__main__":
    insert_fake_data()
