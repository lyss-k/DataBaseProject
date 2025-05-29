import streamlit as st
import duckdb
import pandas as pd

# Connect to your DuckDB database
conn = duckdb.connect('mled_analytics.duckdb', read_only=True)

st.title("Experiment Analytics Dashboard")

st.markdown("""
Welcome to the Experiment Analytics Dashboard. Use the sidebar to filter experiments and explore results, metrics, and dataset information.
""")

# Load full data (adjust table name as needed)
TABLE_NAME = "experiment_flat" 
try:
    df = conn.execute(f"SELECT * FROM {TABLE_NAME}").fetchdf()
except Exception as e:
    st.error(f"Error loading table `{TABLE_NAME}`: {e}")
    st.stop()

# Sidebar filters
st.sidebar.header("Filter Experiments")
st.sidebar.markdown("Use these filters to select and view data for specific experiments.")
experiment_names = df['Experiment_Name'].dropna().unique()
selected_experiment = st.sidebar.selectbox("Select Experiment", ["All"] + sorted(experiment_names))

if selected_experiment != "All":
    df = df[df['Experiment_Name'] == selected_experiment]

# Basic stats
st.header("Experiment Summary")
st.markdown("""
This section provides a summary of the selected experiment, including the number of trials, models, and types of metrics collected.
""")
st.write("Number of Trials:", df['Trial_ID'].nunique())
st.write("Number of Models:", df['Model_ID'].nunique())
st.write("Metric Types Collected:", df['Metric_Name'].unique())

# Metric plot
st.subheader("Metric Over Time")
st.markdown("""
Visualize how a selected metric changes over time during the experiment trials.
""")
metric_options = df['Metric_Name'].dropna().unique()
if len(metric_options) > 0:
    metric_to_plot = st.selectbox("Select Metric", metric_options)
    metric_df = df[df['Metric_Name'] == metric_to_plot].copy()

    if not metric_df.empty:
        metric_df['Metric_Timestamp'] = pd.to_datetime(metric_df['Metric_Timestamp'], errors='coerce')
        metric_df = metric_df.dropna(subset=['Metric_Timestamp']).sort_values('Metric_Timestamp')
        st.line_chart(metric_df[['Metric_Timestamp', 'Metric_Value']].set_index('Metric_Timestamp'))
else:
    st.warning("No metrics found to plot.")

# Hyperparameter analysis
st.subheader("Hyperparameter Distribution")
st.markdown("""
Analyze the distribution of metric values for different hyperparameter settings.
""")
hyperparam_options = df['Hyperparameter_Type'].dropna().unique()
if len(hyperparam_options) > 0:
    hyperparam_to_plot = st.selectbox("Select Hyperparameter", hyperparam_options)
    hyper_df = df[df['Hyperparameter_Type'] == hyperparam_to_plot]

    if not hyper_df.empty:
        bar_data = hyper_df.groupby('Hyperparameter_Value')['Metric_Value'].mean().sort_index()
        st.bar_chart(bar_data)
else:
    st.warning("No hyperparameter data available.")

# Dataset summary
st.subheader("Datasets Used")
st.markdown("""
See which datasets were used in the experiments, along with their versions and sizes.
""")
dataset_cols = ['Dataset_Name', 'Dataset_Version', 'Dataset_Size']
available_cols = [col for col in dataset_cols if col in df.columns]

if available_cols:
    st.dataframe(df[available_cols].drop_duplicates())
else:
    st.info("Dataset columns not found in table.")
