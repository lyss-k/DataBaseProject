import sqlite3
import logging
import uuid
from datetime import datetime

#enter UUIDs

logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')


def connect_db(database_name="test.db"):
    """Establish a connection to the SQLite database."""
    return sqlite3.connect(database_name)


def execute_query(query, params=()):
    """Execute a single query with error handling."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
    except sqlite3.IntegrityError as e:
        logging.error(f"Integrity error: {e}")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    except Exception as e:
        logging.error(f"Exception: {e}")
    finally:
        conn.close()

def fetch_data(query, params=()):
    """Retrieve data from the database with error handling."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return []
    except Exception as e:
        logging.error(f"Exception: {e}")
        return []
    finally:
        conn.close()


def insert_user(first_name, last_name, email, role):
    """Insert a new user into the User table with validation."""
    if not first_name or not email or not role:
        logging.error("Error: First name, email, and role are required.")
        return
    user_id = str(uuid.uuid4())
    query = """
    INSERT INTO User (User_ID, First_Name, Last_Name, Email, Role) VALUES (?, ?, ?, ?, ?)"""
    execute_query(query, (user_id, first_name, last_name, email, role))

def insert_dataset(name, version, description, storage_location, size):
    """Insert a new dataset into the Dataset table with validation."""
    if not name or not description or not storage_location or size <= 0:
        logging.error("Error: Name, description, storage location, and a valid size are required.")
        return
    data_id = str(uuid.uuid4())
    query = """
    INSERT INTO Dataset (DataSet_ID, Name, Version, Description, Storage_Location, Size) VALUES (?, ?, ?, ?, ?, ?)"""
    execute_query(query, (data_id, name, version, description, storage_location, size))

def insert_model(name, model_type, version, hyperparameters, artifact_location):
    """Insert a new model into the Model table with validation."""
    if not name or not model_type or not artifact_location:
        logging.error("Error: Name, model type, and artifact location are required.")
        return
    model_id = str(uuid.uuid4())
    query = """
    INSERT INTO Model (Model_ID, Name, Type, Version, Hyperparameters, ArtifactLocation) VALUES (?, ?, ?, ?, ?, ?)"""
    execute_query(query, (model_id, name, model_type, version, hyperparameters, artifact_location))

def insert_experiment(name, author_id, description, status, model_id, dataset_id):
    """Insert a new experiment into the Experiment table with validation."""
    if not name or not author_id or not description or not status or not model_id or not dataset_id:
        logging.error("Error: All fields are required for inserting an experiment.")
        return
    start_time = datetime.now()
    end_time = datetime.now()
    experiment_id = str(uuid.uuid4())
    query = """
    INSERT INTO Experiment (Experiment_ID, Name, Author_ID, Description, StartTimeStamp, EndTimeStamp, Status, Model_ID, DataSet_ID) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    execute_query(query, (experiment_id, name, author_id, description, start_time, end_time, status, model_id, dataset_id))

def insert_trial(experiment_id, status, start_time, end_time, seed):
    """Insert a new trial into the Trial table with validation."""
    if not experiment_id or not status or not start_time or not end_time:
        logging.error("Error: Experiment ID, status, start time, and end time are required.")
        return
    trial_id = str(uuid.uuid4())
    query = """
    INSERT INTO Trial (Trial_ID, Experiment_ID, Status, StartTime, EndTime, Seed) VALUES (?, ?, ?, ?, ?, ?)"""
    execute_query(query, (trial_id, experiment_id, status, start_time, end_time, seed))

def insert_metric(trial_id, name, value, timestamp):
    """Insert a new metric into the Metric table with validation."""
    if not trial_id or not name or value is None or not timestamp:
        logging.error("Error: Trial ID, name, value, and timestamp are required.")
        return
    metric_id = str(uuid.uuid4())
    query = """
    INSERT INTO Metric (Metric_ID, Trial_ID, Name, Value, TimeStamp) VALUES (?, ?, ?, ?, ?)"""
    execute_query(query, (metric_id, trial_id, name, value, timestamp))

def insert_hyperparameter(trial_id, param_type, epochs, value):
    """Insert a new hyperparameter into the Hyperparameter table with validation."""
    if not trial_id or not param_type or value is None:
        logging.error("Error: Trial ID, type, and value are required.")
        return
    hyper_id = str(uuid.uuid4())
    query = """
    INSERT INTO Hyperparameter (Hyperparameter_ID, Trial_ID, Type, Epochs, Value) VALUES (?, ?, ?, ?, ?)"""
    execute_query(query, (hyper_id, trial_id, param_type, epochs, value))

def insert_error_log(experiment_id, trial_id, timestamp, error_message, error_details):
    """Insert a new error log into the ErrorLog table with validation."""
    if not experiment_id or not trial_id or not timestamp or not error_message or not error_details:
        logging.error("Error: Experiment ID, trial ID, timestamp, error message, and error details are required.")
        return
    error_id = str(uuid.uuid4())
    query = """
    INSERT INTO ErrorLog (Error_ID, Experiment_ID, Trial_ID, TimeStamp, ErrorMessage, ErrorDetails) VALUES (?, ?, ?, ?, ?, ?)"""
    execute_query(query, (error_id, experiment_id, trial_id, timestamp, error_message, error_details))

def update_value(table, column, new_value, condition_column, condition_value):
    """Update a specific column in a table based on a condition, logging errors if no record is found."""
    check_query = f"SELECT COUNT(*) FROM {table} WHERE {condition_column} = ?"
    existing_count = fetch_data(check_query, (condition_value,))[0][0]

    if existing_count == 0:
        logging.error(f"Update failed: No record found in {table} where {condition_column} = {condition_value}")
        return

    query = f"UPDATE {table} SET {column} = ? WHERE {condition_column} = ?"
    execute_query(query, (new_value, condition_value))


def fetch_table(table):
    """Retrieve all rows from a specified table."""
    query = f"SELECT * FROM {table}"
    return fetch_data(query)

def delete_row(table, condition_column, condition_value):
    """Delete a row from a table based on a condition, logging an error if no record exists."""
    
    check_query = f"SELECT COUNT(*) FROM {table} WHERE {condition_column} = ?"
    record_exists = fetch_data(check_query, (condition_value,))[0][0] > 0  # Returns True if record exists
    
    if not record_exists:
        logging.error(f"Delete failed: No record found in {table} where {condition_column} = {condition_value}")
        return 

    query = f"DELETE FROM {table} WHERE {condition_column} = ?"
    execute_query(query, (condition_value,))

def delete_table(table):
    """Delete an entire table from the database."""
    query = f"DROP TABLE IF EXISTS {table}"
    execute_query(query)

def fetch_experiments_by_author(author_id):
    """Retrieve all experiments associated with a given author ID."""
    query = "SELECT * FROM Experiment WHERE Author_ID = ?"
    return fetch_data(query, (author_id,))

def count_records(table):
    """Count the number of records in a given table."""
    query = f"SELECT COUNT(*) FROM {table}"
    return fetch_data(query)[0][0]

def get_latest_experiment():
    """Retrieve the most recently created experiment."""
    query = "SELECT * FROM Experiment ORDER BY StartTimeStamp DESC LIMIT 1"
    return fetch_data(query)

def get_active_experiments():
    """Retrieve all experiments that are currently active."""
    query = "SELECT * FROM Experiment WHERE Status = 'Active'"
    return fetch_data(query)

#test
#insert_user("Tilly", "White", "email7@email", "Data Scientist")
#delete_record("User", "4ecd6f11-446f-4730-8e6e-ec218421d0b4")
#insert_dataset("name", 2, "description", "storage_location", 40000)
#update_value("User", "First_Name", "Fink", "First_Name", "Jacklyn")