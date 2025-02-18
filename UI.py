from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import uuid
from datetime import datetime

app = Flask(__name__)
DATABASE = "test.db"

# Helper function to connect to SQLite
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return render_template('index.html', tables=tables)

# Route to create a new user
@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        user_id = str(uuid.uuid4())
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        role = request.form['role']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO User (User_ID, First_Name, Last_Name, Email, Role) VALUES (?, ?, ?, ?, ?)",
                           (user_id, first_name, last_name, email, role))
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            return jsonify({"error": str(e)})
        finally:
            conn.close()
        
        return jsonify({"message": "User created successfully", "user_id": user_id})
    return render_template('create_user.html')

# Route to log new experiment along with dataset and model
@app.route('/log_experiment', methods=['GET', 'POST'])
def log_experiment_route():
    if request.method == 'POST':
        name = request.form['name']
        author_id = request.form['author_id']
        description = request.form['description']
        status = request.form['status']
        
        # Dataset details
        dataset_id = str(uuid.uuid4())
        dataset_name = request.form['dataset_name']
        dataset_version = request.form['dataset_version']
        dataset_description = request.form['dataset_description']
        dataset_location = request.form['dataset_location']
        dataset_size = request.form['dataset_size']
        
        # Model details
        model_id = str(uuid.uuid4())
        model_name = request.form['model_name']
        model_type = request.form['model_type']
        model_version = request.form['model_version']
        model_hyperparameters = request.form['model_hyperparameters']
        model_artifact_location = request.form['model_artifact_location']
        
        experiment_id = str(uuid.uuid4())
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Insert dataset
            cursor.execute("INSERT INTO Dataset (DataSet_ID, Name, Version, Description, Storage_Location, Size) VALUES (?, ?, ?, ?, ?, ?)",
                           (dataset_id, dataset_name, dataset_version, dataset_description, dataset_location, dataset_size))
            
            # Insert model
            cursor.execute("INSERT INTO Model (Model_ID, Name, Type, Version, Hyperparameters, ArtifactLocation) VALUES (?, ?, ?, ?, ?, ?)",
                           (model_id, model_name, model_type, model_version, model_hyperparameters, model_artifact_location))
            
            # Insert experiment
            cursor.execute("INSERT INTO Experiment (Experiment_ID, Name, Author_ID, Description, StartTimeStamp, Status, Model_ID, DataSet_ID) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (experiment_id, name, author_id, description, start_time, status, model_id, dataset_id))
            
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            return jsonify({"error": str(e)})
        finally:
            conn.close()
        
        return jsonify({"message": "Experiment logged successfully", "experiment_id": experiment_id})
    return render_template('log_experiment.html')

@app.route('/get_trials')
def get_trials():
    experiment_id = request.args.get('experiment_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Trial_ID FROM Trial WHERE Experiment_ID = ?", (experiment_id,))
    trials = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify({"trials": trials})

# Route to add data to an existing experiment or trial
@app.route('/add_experiment_data', methods=['GET', 'POST'])
def add_experiment_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Experiment_ID, Name FROM Experiment")
    experiments = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    
    selected_experiment = request.args.get('experiment_id')
    trials = []
    if selected_experiment:
        cursor.execute("SELECT Trial_ID FROM Trial WHERE Experiment_ID = ?", (selected_experiment,))
        trials = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    if request.method == 'POST':
        experiment_id = request.form['experiment_id']
        trial_id = request.form.get('trial_id')
        data_type = request.form['data_type']
        name = request.form.get('name', '')
        value = request.form.get('value', '')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = request.form.get('status', 'Running')
        error_details = request.form.get('error_details', '')
        end_time = request.form.get('end_time', None)
        epochs = request.form.get('epochs', None)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if data_type == 'error':
                cursor.execute("INSERT INTO ErrorLog (Error_ID, Experiment_ID, Trial_ID, TimeStamp, ErrorMessage, ErrorDetails) VALUES (?, ?, ?, ?, ?, ?)",
                               (str(uuid.uuid4()), experiment_id, trial_id, timestamp, value, error_details))
            elif data_type == 'trial':
                cursor.execute("INSERT INTO Trial (Trial_ID, Experiment_ID, Status, StartTime, EndTime, SEE) VALUES (?, ?, ?, ?, ?, ?)",
                               (str(uuid.uuid4()), experiment_id, status, timestamp, end_time, value))
            elif data_type == 'metric':
                cursor.execute("INSERT INTO Metric (Metric_ID, Trial_ID, Name, Value, TimeStamp) VALUES (?, ?, ?, ?, ?)",
                               (str(uuid.uuid4()), trial_id, name, value, timestamp))
            elif data_type == 'hyperparameter':
                cursor.execute("INSERT INTO Hyperparameter (Hyperparameter_ID, Trial_ID, Type, Epochs, Value) VALUES (?, ?, ?, ?, ?)",
                               (str(uuid.uuid4()), trial_id, name, epochs, value))
            
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            return jsonify({"error": str(e)})
        finally:
            conn.close()
        
        return jsonify({"message": "Data added successfully"})
    return render_template('add_experiment_data.html', experiments=experiments, trials=trials)



# Route to execute raw SQL queries
@app.route('/query_experiments', methods=['GET', 'POST'])
def query_experiments():
    conn = get_db_connection()
    cursor = conn.cursor()
    results = []
    error = None
    
    if request.method == 'POST':
        sql_query = request.form.get('sql_query', '').strip()
        if sql_query:
            try:
                cursor.execute(sql_query)
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
            except sqlite3.Error as e:
                error = f"SQL Error: {str(e)}"
    
    conn.close()
    return render_template('query_experiments.html', results=results, error=error)

def get_all_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def get_table_data(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT * FROM {table_name};"
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]  # Get column names
    conn.close()
    return columns, rows

@app.route('/database_overview')
def database_overview():
    tables = get_all_tables()
    table_data = {}
    for table in tables:
        columns, rows = get_table_data(table)
        table_data[table] = {"columns": columns, "rows": rows}
    return render_template("database_overview.html", tables=table_data)


if __name__ == '__main__':
    app.run(debug=True)
