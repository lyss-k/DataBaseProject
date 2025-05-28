import streamlit as st
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

# Connect to your DuckDB database
conn = duckdb.connect('your_database.duckdb')

st.title("Experiment Analytics Dashboard")

# Load full data (you can optimize with SQL views or WHERE clauses later)
df = conn.execute("SELECT * FROM your_table").df()

# Sidebar filters
st.sidebar.header("Filter Experiments")
experiment_names = df['Experiment_Name'].dropna().unique()
selected_experiment = st.sidebar.selectbox("Select Experiment", ["All"] + list(experiment_names))

if selected_experiment != "All":
    df = df[df['Experiment_Name'] == selected_experiment]

# Basic stats
st.header("Experiment Summary")
st.write("Number of Trials:", df['Trial_ID'].nunique())
st.write("Number of Models:", df['Model_ID'].nunique())
st.write("Metric Types Collected:", df['Metric_Name'].unique())

# Metric plot
st.subheader("Metric Over Time")
metric_to_plot = st.selectbox("Select Metric", df['Metric_Name'].unique())
metric_df = df[df['Metric_Name'] == metric_to_plot]

if not metric_df.empty:
    metric_df['Metric_Timestamp'] = pd.to_datetime(metric_df['Metric_Timestamp'])
    metric_df = metric_df.sort_values('Metric_Timestamp')
    st.line_chart(metric_df[['Metric_Timestamp', 'Metric_Value']].set_index('Metric_Timestamp'))

# Hyperparameter analysis
st.subheader("Hyperparameter Distribution")
hyperparam_to_plot = st.selectbox("Select Hyperparameter", df['Hyperparameter_Type'].dropna().unique())
hyper_df = df[df['Hyperparameter_Type'] == hyperparam_to_plot]

if not hyper_df.empty:
    st.bar_chart(hyper_df.groupby('Hyperparameter_Value')['Metric_Value'].mean())

# Dataset summary
st.subheader("Datasets Used")
st.dataframe(df[['Dataset_Name', 'Dataset_Version', 'Dataset_Size']].drop_duplicates())