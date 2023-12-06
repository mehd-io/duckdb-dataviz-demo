import streamlit as st
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

# Connect to your DuckDB database
con = duckdb.connect(database='duckdb_stats.db', read_only=True)

# Streamlit page configuration
st.title("DuckDB pypi stats")

# Date Window Filter
min_date, max_date = con.execute("SELECT MIN(timestamp_day), MAX(timestamp_day) FROM duckdb_stats.main.daily_stats").fetchone()
start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Query for filtered data
query = """
SELECT 
    DATE_TRUNC('month', timestamp_day) AS month, 
    SUM(daily_download_count) AS total_downloads,
    python_version,
    cpu
FROM duckdb_stats.main.daily_stats
WHERE timestamp_day BETWEEN ? AND ?
GROUP BY month, python_version, cpu
ORDER BY month
"""
df = con.execute(query, (start_date, end_date)).df()

# Total Downloads
total_downloads = df['total_downloads'].sum()

# Function to format numbers for readability
def human_readable_number(num):
    for unit in ['', 'K', 'M', 'B']:
        if abs(num) < 1000:
            return f"{num:.0f}{unit}"
        num /= 1000
    return f"{num:.0f}T"

st.metric("Total Downloads", human_readable_number(total_downloads))

# Line Graph of Downloads Over Time
st.subheader("Monthly Downloads Over Time")
df_monthly = df.groupby('month')['total_downloads'].sum().reset_index()
st.line_chart(df_monthly.set_index('month'))

# Line Graph of Python Versions Usage
st.subheader("Python Version Usage Over Time")
df_python_version = df.groupby(['month', 'python_version'])['total_downloads'].sum().unstack().fillna(0)
st.line_chart(df_python_version)

# CPU Usage Table
st.subheader("CPU Usage Summary")
df_cpu = df.groupby(['cpu'])['total_downloads'].sum().reset_index()
df_cpu['Percentage'] = (df_cpu['total_downloads'] / total_downloads) * 100
df_cpu = df_cpu.sort_values(by='total_downloads', ascending=False)
st.table(df_cpu.style.format({'total_downloads': '{:,.0f}', 'Percentage': '{:.2f}%'}))
