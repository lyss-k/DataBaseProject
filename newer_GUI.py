import justpy as jp
import database_operations as db_ops
import csv
import io
import base64

def submit_form(self, msg):
    """Handles form submission and inserts data into the database."""
    table = self.table_name
    fields = self.fields
    inputs = self.inputs
    
    data = {field: inputs[field].value for field in fields}
    
    if table == "User":
        db_ops.insert_user(data['First_Name'], data['Last_Name'], data['Email'], data['Role'])
    elif table == "Dataset":
        db_ops.insert_dataset(data['Name'], int(data['Version']), data['Description'], data['Storage_Location'], int(data['Size']))
    elif table == "Model":
        db_ops.insert_model(data['Name'], data['Type'], int(data['Version']), data['Hyperparameters'], data['ArtifactLocation'])
    elif table == "Experiment":
        db_ops.insert_experiment(data['Name'], data['Author_ID'], data['Description'], data['Status'], data['Model_ID'], data['DataSet_ID'])
    elif table == "Trial":
        db_ops.insert_trial(data['Experiment_ID'], data['Status'], data['Start_Time'], data['End_Time'], int(data['Seed']))
    elif table == "Metric":
        db_ops.insert_metric(data['Trial_ID'], data['Name'], int(data['Value']), data['TimeStamp'])
    elif table == "Hyperparameter":
        db_ops.insert_hyperparameter(data['Trial_ID'], data['Type'], int(data['Epochs']), float(data['Value']))
    elif table == "ErrorLog":
        db_ops.insert_error_log(data['Experiment_ID'], data['Trial_ID'], data['TimeStamp'], data['ErrorMessage'], data['ErrorDetails'])
    
    msg.page.add(jp.Div(text=f"Data added to {table} successfully!"))

def create_form(table_name, fields, dropdown_data=None):
    """Generates a form for a given table with enforced dropdown selection."""
    wp = jp.WebPage()
    container = jp.Div(classes="m-4 p-4 border", a=wp)
    
    jp.H2(text=f"Enter data for {table_name}", classes="text-lg font-bold", a=container)
    inputs = {}
    
    for field in fields:
        jp.Label(text=field, a=container)
        if dropdown_data and field in dropdown_data:
            input_box = jp.Select(a=container, classes="border p-2 m-2")
            jp.Option(value="", text="Select an option", a=input_box, disabled=True, selected=True)
            for option in dropdown_data[field]:
                jp.Option(value=option[0], text=option[1], a=input_box)
            inputs[field] = input_box
        else:
            input_box = jp.Input(classes="border p-2 m-2", a=container)
            inputs[field] = input_box
    
    submit_button = jp.Button(text="Submit", classes="bg-blue-500 text-white p-2 m-2", a=container)
    submit_button.table_name = table_name
    submit_button.fields = fields
    submit_button.inputs = inputs
    submit_button.on('click', submit_form)
    
    return wp

def experiment_form():
    models = db_ops.fetch_table("Model")
    model_options = [(row[0], row[1]) for row in models]  # (Model_ID, Name)
    return create_form("Experiment", ["Name", "Author_ID", "Description", "Status", "Model_ID", "DataSet_ID"], dropdown_data={"Model_ID": model_options})

def trial_form():
    experiments = db_ops.fetch_table("Experiment")
    experiment_options = [(row[0], row[1]) for row in experiments]  # (Experiment_ID, Name)
    return create_form("Trial", ["Experiment_ID", "Status", "Start_Time", "End_Time", "Seed"], dropdown_data={"Experiment_ID": experiment_options})

def metric_form():
    trials = db_ops.fetch_table("Trial")
    trial_options = [(row[0], row[0]) for row in trials]  # (Trial_ID, Trial_ID)
    return create_form("Metric", ["Trial_ID", "Name", "Value", "TimeStamp"], dropdown_data={"Trial_ID": trial_options})

def hyperparameter_form():
    trials = db_ops.fetch_table("Trial")
    trial_options = [(row[0], row[0]) for row in trials]  # (Trial_ID, Trial_ID)
    return create_form("Hyperparameter", ["Trial_ID", "Type", "Epochs", "Value"], dropdown_data={"Trial_ID": trial_options})

def errorlog_form():
    trials = db_ops.fetch_table("Trial")
    trial_options = [(row[0], row[0]) for row in trials]  # (Trial_ID, Trial_ID)
    return create_form("ErrorLog", ["Experiment_ID", "Trial_ID", "TimeStamp", "ErrorMessage", "ErrorDetails"], dropdown_data={"Trial_ID": trial_options})

def homepage():
    """Creates a homepage listing all available routes."""
    wp = jp.WebPage()
    container = jp.Div(classes="m-4 p-4 border", a=wp)
    wp.classes = "bg-gray-900 text-white min-h-screen flex flex-col items-center justify-center p-10"
    
    container = jp.Div(classes="text-center", a=wp)
    jp.H1(text="Welcome to the ML Experiment Database Management Interface", classes="text-3xl font-bold text-blue-400 mb-2", a=container)
    jp.P(text="Manage your data with ease using our modern interface.", classes="text-gray-400 mb-6", a=container)
    
    routes = [
        ("User Form", "/user"),
        ("Dataset Form", "/dataset"),
        ("Model Form", "/model"),
        ("Experiment Form", "/experiment"),
        ("Trial Form", "/trial"),
        ("Metric Form", "/metric"),
        ("Hyperparameter Form", "/hyperparameter"),
        ("ErrorLog Form", "/errorlog"),
        ("Show Database", "/show_database"),
        ("Query Database", "/query_database")
    ]
    
    for name, route in routes:
        jp.A(text=name, href=route, classes="bg-blue-500 hover:bg-blue-600 text-white p-3 rounded-lg m-2 inline-block", a=container)
    
    return wp

def user_form():
    return create_form("User", ["First_Name", "Last_Name", "Email", "Role"])

def dataset_form():
    return create_form("Dataset", ["Name", "Version", "Description", "Storage_Location", "Size"])

def model_form():
    return create_form("Model", ["Name", "Type", "Version", "Hyperparameters", "ArtifactLocation"])

def show_database():
    """Displays all tables in the database with formatted output."""
    wp = jp.WebPage()
    container = jp.Div(classes="m-4 p-4 border", a=wp)
    jp.H2(text="Database Content", classes="text-lg font-bold", a=container)
    
    tables = ["User", "Dataset", "Model", "Experiment", "Trial", "Metric", "Hyperparameter", "ErrorLog"]
    
    for table in tables:
        jp.H3(text=f"Table: {table}", classes="text-md font-bold mt-4", a=container)
        column_info = db_ops.fetch_data(f"PRAGMA table_info({table})")
        column_names = [col[1] for col in column_info] if column_info else []
        data = db_ops.fetch_data(f"SELECT * FROM {table}")
        
        if data:
            table_element = jp.Table(classes="border-collapse border border-gray-300 w-full", a=container)
            header_row = jp.Tr(classes="bg-gray-200", a=table_element)
            
            for col in column_names:
                jp.Th(text=col, classes="border border-gray-400 p-2", a=header_row)
            
            for row in data:
                tr = jp.Tr(a=table_element)
                for cell in row:
                    jp.Td(text=str(cell), classes="border border-gray-300 p-2", a=tr)
        else:
            jp.P(text="No data available.", classes="text-gray-500", a=container)
    
    return wp

def get_columns_for_table(table):
    """Retrieve column names for a given table."""
    query = f"PRAGMA table_info({table})"
    return [row[1] for row in db_ops.fetch_data(query)]

def query_database():
    """Allows users to execute predefined queries or input their own SQL queries and download results."""
    wp = jp.WebPage()
    container = jp.Div(classes="m-4 p-4 border", a=wp)
    
    jp.H2(text="Query Database", classes="text-lg font-bold", a=container)
    
    predefined_queries = {
        "Fetch All Users": "SELECT * FROM User",
        "Fetch All Experiments": "SELECT * FROM Experiment",
        "Fetch Active Experiments": "SELECT * FROM Experiment WHERE Status = 'Active'",
        "Count Records in Model": "SELECT COUNT(*) FROM Model",
        "Latest Experiment": "SELECT * FROM Experiment ORDER BY StartTimeStamp DESC LIMIT 1"
    }
    
    query_select = jp.Select(classes="border p-2 m-2", a=container)
    jp.Option(value="", text="Select a predefined query", a=query_select, disabled=True, selected=True)
    for label, query in predefined_queries.items():
        jp.Option(value=query, text=label, a=query_select)
    
    custom_query_input = jp.Textarea(placeholder="Enter your SQL query here", classes="border p-2 m-2 w-full h-24", a=container)
    
    result_div = jp.Div(classes="mt-4", a=container)
    download_link = jp.A(text="Download Results", href="#", classes="hidden text-blue-500 underline mt-2", a=container)
    
    def run_query(self, msg):
        result_div.delete_components()
        query = query_select.value or custom_query_input.value.strip()
        
        if not query:
            result_div.add(jp.P(text="Please enter a valid query or select a predefined one."))
            return
        
        try:
            data = db_ops.fetch_data(query)
            if not data:
                result_div.add(jp.P(text="No results found."))
                download_link.classes = "hidden"
            else:
                table_element = jp.Table(classes="border-collapse border border-gray-300 w-full", a=result_div)
                for row in data:
                    tr = jp.Tr(a=table_element)
                    for cell in row:
                        jp.Td(text=str(cell), classes="border border-gray-300 p-2", a=tr)
                
                # Generate CSV file
                csv_output = io.StringIO()
                csv_writer = csv.writer(csv_output)
                csv_writer.writerows(data)
                csv_content = csv_output.getvalue().encode('utf-8')
                csv_base64 = base64.b64encode(csv_content).decode('utf-8')
                
                download_link.href = f"data:text/csv;base64,{csv_base64}"
                download_link.download = "query_results.csv"
                download_link.classes = "text-blue-500 underline mt-2"
        except Exception as e:
            result_div.add(jp.P(text=f"Error: {str(e)}", classes="text-red-500"))
            download_link.classes = "hidden"
    
    query_button = jp.Button(text="Run Query", classes="bg-blue-500 text-white p-2 m-2", a=container)
    query_button.on('click', run_query)
    
    return wp

def main():
    jp.Route("/", homepage)
    jp.Route("/user", lambda: create_form("User", ["First_Name", "Last_Name", "Email", "Role"]))
    jp.Route("/dataset", lambda: create_form("Dataset", ["Name", "Version", "Description", "Storage_Location", "Size"]))
    jp.Route("/model", lambda: create_form("Model", ["Name", "Type", "Version", "Hyperparameters", "ArtifactLocation"]))
    jp.Route("/experiment", experiment_form)
    jp.Route("/trial", trial_form)
    jp.Route("/metric", metric_form)
    jp.Route("/hyperparameter", hyperparameter_form)
    jp.Route("/errorlog", errorlog_form)
    jp.Route("/show_database", show_database)
    jp.Route("/query_database", query_database)
    jp.justpy()

if __name__ == "__main__":
    main()