import streamlit as st
import pandas.io.sql as sqlio
import psycopg2  # or another database adapter depending on your DB, e.g., sqlite3, mysql.connector
import altair as alt
import folium
import pandas as pd
from streamlit_folium import st_folium
import os

st.title("Seattle Events Analysis")

# Establish a database connection (example using psycopg2 for PostgreSQL)
# Ensure you replace 'your_connection_string' with your actual connection string

from db import conn_str as conn

# Task 1.A: What category of events are most common in Seattle?
df_category = sqlio.read_sql_query("SELECT category, COUNT(*) as event_count FROM events GROUP BY category ORDER BY event_count DESC", conn)
st.subheader("🎵 Most Common Event Categories in Seattle")
chart1 = alt.Chart(df_category).mark_bar().encode(
    x=alt.X("category:N", sort='-y'),
    y=alt.Y("event_count:Q", title="Number of Events"),
    tooltip=["category:N", "event_count:Q"]
).interactive()
st.altair_chart(chart1, use_container_width=True)

# Task 1.B: What month has the most number of events?
df_month = sqlio.read_sql_query("SELECT EXTRACT(MONTH FROM date) AS month, COUNT(*) as event_count FROM events GROUP BY month ORDER BY event_count DESC", conn)
st.subheader("🪴 Months with Most Events")
chart2 = alt.Chart(df_month).mark_bar().encode(
    x=alt.X("month:N", title="Month"),
    y=alt.Y("event_count:Q", title="Number of Events"),
    tooltip=["month:N", "event_count:Q"]
).interactive()
st.altair_chart(chart2, use_container_width=True)

# Task 1.C: What day of the week has the most number of events?
df_day_of_week = sqlio.read_sql_query("SELECT EXTRACT(DOW FROM date) AS day_of_week, COUNT(*) as event_count FROM events GROUP BY day_of_week ORDER BY event_count DESC", conn)
st.subheader("🌈 Most Common Days for Events")
chart3 = alt.Chart(df_day_of_week).mark_bar().encode(
    x=alt.X("day_of_week:N", title="Day of the Week"),
    y=alt.Y("event_count:Q", title="Number of Events"),
    tooltip=["day_of_week:N", "event_count:Q"]
).interactive()
st.altair_chart(chart3, use_container_width=True)

# Preprocess geolocation into separate latitude and longitude columns
query = "SELECT * FROM events"
df = sqlio.read_sql_query(query, conn)

df[['latitude', 'longitude']] = df['geolocation'].str.extract(r'\{([^,]+),([^}]+)\}').astype(float)

# 1. Dropdown to filter by category
category = st.selectbox("Select a category", options=['All'] + sorted(df['category'].unique().tolist()))
if category != 'All':
    df = df[df['category'] == category]

# 2. Date range selector for event date
# Convert 'date' from string to datetime
df['date'] = pd.to_datetime(df['date'])
# default: 2024.01.01 ~ today

start_date, end_date = st.date_input("Select a date range", [df['date'].min(), df['date'].max()])
if start_date and end_date:
    df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]

# 3. Filter by location
location = st.selectbox("Select a location", options=['All'] + sorted(df['location'].unique().tolist()))
if location != 'All':
    df = df[df['location'] == location]

# 4. Filter by weather condition
weather_condition = st.selectbox("Select weather condition", options=['All'] + sorted(df['weathercondition'].unique().tolist()))
if weather_condition != 'All':
    df = df[df['weathercondition'] == weather_condition]

# Assuming you want to visualize some aspect of the filtered data
# For example, showing filtered events on a map
st.subheader("Filtered Event Locations")
m = folium.Map(location=[47.6062, -122.3321], zoom_start=12)
for _, row in df.iterrows():
    folium.Marker([row['latitude'], row['longitude']], popup=row['title']).add_to(m)
st_folium(m, width=730, height=500)
