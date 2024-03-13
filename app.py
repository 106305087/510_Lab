import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from firebase_admin import exceptions
import matplotlib.pyplot as plt
import altair as alt
import pandas as pd
import numpy as np
from datetime import datetime
import time

import os
from llama_index.llms.openai import OpenAI
from openai import Client
from llama_index.core import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader
from dotenv import load_dotenv


load_dotenv()

# Initialize the Firebase Admin SDK
if not firebase_admin._apps:
    firebase_cred = {
        "type": os.environ.get("FIREBASE_TYPE"),
        "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
        "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.environ.get("FIREBASE_PRIVATE_KEY"),
        "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
        "auth_uri": os.environ.get("FIREBASE_AUTH_URI"),
        "token_uri": os.environ.get("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.environ.get("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL"),
        "universe_domain": os.environ.get("FIREBASE_UNIVERSE_DOMAIN"),
    }

    cred = credentials.Certificate(firebase_cred)
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.environ.get("FIREBASE_DB_URL")
    })


st.set_page_config(
    page_title="Rehabilitation Assistant",
    page_icon="💪",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

page = st.sidebar.radio("Choose a view:", ["Historical Record", "Real-time Visualization"])

def fetch_data():
    try:
        ref = db.reference('test/data2')
        pitch_data = ref.get()
        if pitch_data is None:
            return pd.DataFrame(columns=['Timestamp', 'Pitch', 'BendCount', 'GyroY']), True
        data_list = [
            {'Timestamp': v['timestamp'], 'Pitch': v['pitch'], 'BendCount': v['bendCount'], 'GyroY': v['gyroY']}
            for k, v in pitch_data.items()
        ]
        df = pd.DataFrame(data_list)
        
        # Correct unit if necessary (e.g., if in milliseconds)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')  # Adjust unit as needed
        
        # Convert to a specific time zone (from UTC)
        df['Timestamp'] = df['Timestamp'].dt.tz_localize('UTC').dt.tz_convert('America/Los_Angeles')
        
        df.sort_values(by='Timestamp', inplace=True)
        # Select the last 50 records
        # df = df.tail(58)
        return df, True
    except exceptions.FirebaseError:
        return pd.DataFrame(columns=['Timestamp', 'Pitch', 'BendCount', 'GyroY']), False

#### Real-time Plotting---------------------------------------
def display_real_time_plot():
    # st.title('Rehabilitation Data Visualization')
    st.markdown(f"<h1 style='text-align: center'>Real-time Visualization</div>", unsafe_allow_html=True)
    st.text("")
    st.text("")

    last_connect_placeholder = st.empty()
    plot_placeholder = st.empty()
    connection_placeholder = st.empty()
    bend_count_placeholder = st.empty()

    last_data_hash = None
    last_update_time = time.time()

    while True:
        current_time = time.time()
        data, connected = fetch_data()  # Fetch the latest data and check connection status
        data = data.tail(20)

        last_connect_time = f"Last Connection Time: {data.iloc[-1]['Timestamp'].strftime('%Y/%m/%d  %H:%M:%S')}"
        last_connect_placeholder.markdown(f"<h5 style='text-align: center'>{last_connect_time}</div>", unsafe_allow_html=True)
        # st.text("")
        # st.text("")


        if data.empty:
            current_bend_count = "No data available"
        else:
            current_bend_count = data.iloc[-1]['BendCount']

        current_data_hash = pd.util.hash_pandas_object(data).sum()  # Create a hash of the current data for comparison

        # Check if the data has changed or if it's the first iteration
        if current_data_hash != last_data_hash:
            last_update_time = current_time  # Update the last update time to current time
            last_data_hash = current_data_hash  # Update the last data hash
            if connected:
                last_connect_placeholder.empty()
                chart = get_altair_chart(data)  # Create the chart if connected
                plot_placeholder.altair_chart(chart, use_container_width=True)  # Update the plot
                # plot_placeholder.plotly_chart(chart, use_container_width=True)  # Display the Plotly plot
                bend_count_placeholder.markdown(f"**Latest Bend Count:** {current_bend_count}")
                connection_placeholder.markdown("Connected to device")
            else:
                last_connect_placeholder.empty()
                plot_placeholder.empty()  # Clear the plot placeholder
                connection_placeholder.error("Disconnected from device. Trying to reconnect...")

        # Check if it has been more than 15 seconds since the last update
        elif current_time - last_update_time > 15:
            st.text("")
            connection_placeholder.error("Disconnected from device.")

        # If the data hasn't changed but we're within the 15-second window
        else:
            st.text("")
            connection_placeholder.markdown("Connecting...")

        time.sleep(1)  # Wait for a second before fetching again
#### Real-time Plotting---------------------------------------


def get_altair_chart(data):

    data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='s')
    data['MinuteSecond'] = data['Timestamp'].dt.strftime('%M:%S')
    
    # Melt data to long format for Altair
    long_data = data.melt(id_vars=['Timestamp', 'MinuteSecond'], value_vars=['Pitch', 'GyroY'], var_name='Measurement', value_name='Value')
    
    hover = alt.selection_single(
        fields=["Timestamp"],
        nearest=True,
        on="mouseover",
        empty="none",
    )
    
    line_chart = alt.Chart(long_data).mark_line().encode(
        x="Timestamp:T",
        y=alt.Y('Value:Q', axis=alt.Axis(title='Value')),
        color='Measurement:N',
        tooltip=['MinuteSecond', 'Measurement', 'Value']
    ).properties(width=800, height=400)
    
    points = line_chart.transform_filter(hover).mark_circle(size=65)
    
    tooltips = alt.Chart(long_data).mark_rule().encode(
        x='Timestamp:T',
        opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
        tooltip=[
            alt.Tooltip("MinuteSecond:N", title="Time (Min:Sec)"),
            alt.Tooltip("Value:Q", title="Value"),
        ]
    ).add_selection(hover)
    
    return (line_chart + points + tooltips).interactive()

def segment_data_by_time_difference(df):
    segments = []
    start_idx = 0

    # Convert timestamps to datetime if not already done
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    for i in range(1, len(df)):
        # Calculate the difference in minutes between current and previous timestamp
        time_diff = (df.iloc[i]['Timestamp'] - df.iloc[i-1]['Timestamp']).total_seconds() / 60.0

        # If the time difference is more than 10 minutes, segment the data
        if time_diff > 5:
            segment = df.iloc[start_idx:i]
            if not segment.empty:
                segments.append(segment)
            start_idx = i

    # Add the last segment if it exists
    if start_idx < len(df):
        segments.append(df.iloc[start_idx:])

    return segments

def display_historical_data():
    data, connected = fetch_data()  # Fetch all the data, make sure fetch_data fetches all not the last 58
    if not connected or data.empty:
        st.write("Unable to connect to data source or no data available.")
        return

    # Segment the data by bend count
    data_segments = segment_data_by_time_difference(data)
    # print('data_segments')
    # print(data_segments)

    if not data_segments:  # Check if the list is empty
        st.write("No data segments found.")
        return

    # Initialize or update the current segment index
    if 'current_segment_index' not in st.session_state:
        st.session_state.current_segment_index = 0

    #st.subheader('Historical Recodrd')
    st.markdown(f"<h1 style='text-align: center'>Historical Rehab Record</div>", unsafe_allow_html=True)
    st.text("")

    # Display the current segment plot
    current_segment = data_segments[st.session_state.current_segment_index]
    # print('current_segment')
    # print(current_segment)
    
    # Display duration
    start_time = current_segment['Timestamp'].iloc[0]
    end_time = current_segment['Timestamp'].iloc[-1]
    duration_text = f"{start_time.strftime('%Y/%m/%d  %H:%M:%S')} - {end_time.strftime('%H:%M:%S')}"
    st.markdown(f"<h5 style='text-align: center'>{duration_text}</div>", unsafe_allow_html=True)
    st.text("")

    # Display Plot
    chart = get_altair_chart(current_segment)
    st.altair_chart(chart, use_container_width=True)

    # Pagination
    max_index = len(data_segments) - 1
    pagination_text = f"Page {st.session_state.current_segment_index + 1} of {len(data_segments)}"

    # Navigation buttons
    col_prev, col_pagination, col_next = st.columns([4, 3.5, 1])
    with col_prev:
        if st.button("Previous") and st.session_state.current_segment_index > 0:
            st.session_state.current_segment_index -= 1
            st.experimental_rerun()  # Rerun the app to refresh the plot
    with col_pagination:
        st.write(pagination_text)  # Displaying current page info in the middle
    with col_next:
        if st.button("Next") and st.session_state.current_segment_index < max_index:
            st.session_state.current_segment_index += 1
            st.experimental_rerun()  # Rerun the app to refresh the plot
    
    # Data summary
    st.text("")
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center'>📝 Summary 📝</div>", unsafe_allow_html=True)
    ROM = current_segment['Pitch'].max() - current_segment['Pitch'].min()
    gyro_std = current_segment['GyroY'].std()
    bend_count = current_segment['BendCount'].max()
    time_range = (end_time - start_time).seconds / 60
    jerk_avg = abs((np.diff(current_segment['Pitch'], n=2)).mean())
    speed_avg = abs(current_segment['GyroY'].mean())


    # pitch_text = f"Range of Movement (ROM): {ROM:.2f}  degree"
    # SD_text = f"Smoothness: {gyro_std:.2f}"
    # time_text = f"Duration: {time_range:.2f} minutes"
    st.text("")
    col1, col2, col3 = st.columns([1.2, 1.2, 1])
    with col1:
        st.write(f"Number of Bends: {bend_count}")
        st.write(f"Duration: {time_range:.2f} minutes")
    with col2:
        st.write(f"ROM: {ROM:.2f}  degree")
        st.write(f"Smoothness: {gyro_std:.2f}")
    with col3:
        st.write(f"Consistency: {jerk_avg:.2f}")
        st.write(f"Average Speed: {speed_avg:.2f}")

def chatbot(data_segments):
    st.text("")
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center'>🤖 Chat with AI 🤖</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align: center;'><span style='color: grey;'>Click the buttons to get quick insights!</span></div>", unsafe_allow_html=True)
    st.text("")
    # Set OpenAI API key from Streamlit secrets
    client = Client(api_key=os.getenv("OPENAI_API_KEY"),
                    base_url=os.getenv("OPENAI_API_BASE"),
                ) 

    # Set a default model
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo-0125"

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    def process_message(prompt):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add a system message to customize the chatbot's response
        system_message = "You are a physical therapist. Please provide a response in bullet points."
        st.session_state.messages.append({"role": "system", "content": system_message})

        with st.spinner("Thinking..."):
            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                )
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                print('----------message---------')
                print(message)
                if message["role"] == "user" and 'information' in message["content"]:
                    # Display the button prompt instead of the long data text
                    st.markdown("Explain Plot")
                elif message["role"] == "user" and 'Endurance' in message["content"]:
                    st.markdown("Summarize Data")
                else:
                    st.markdown(message["content"])
    
    # Button for explaining the data
    if st.button("Explain Plot"):
        # Gather data from current segment
        current_segment = data_segments[st.session_state.current_segment_index]
        data_text = current_segment.to_string(index=False)
        prompt = data_text + '\n\n' + 'Please explain the data. Include information about the Range of Movement (ROM), Smoothness, and Duration of the workout'
        st.session_state.messages.append({"role": "user", "content": prompt})
        process_message("Explain Plot")
    
    
    if st.button("Summarize Data"):
        # Gather data from current segment
        current_segment = data_segments[st.session_state.current_segment_index]
        # Calculate summary statistics
        start_time = current_segment['Timestamp'].iloc[0]
        end_time = current_segment['Timestamp'].iloc[-1]
        ROM = current_segment['Pitch'].max() - current_segment['Pitch'].min()
        gyro_std = current_segment['GyroY'].std()
        bend_count = current_segment['BendCount'].max()
        time_range = (end_time - start_time).seconds / 60
        jerk_avg = abs((np.diff(current_segment['Pitch'], n=2)).mean())
        speed_avg = abs(current_segment['GyroY'].mean())

        # Create summary text
        summary_text = (
            f"Number of Bends: {bend_count}\n"
            f"Duration: {time_range:.2f} minutes\n"
            f"Range of Movement (ROM): {ROM:.2f} degrees\n"
            f"Smoothness: {gyro_std:.2f}\n"
            f"Consistency: {jerk_avg:.2f}\n"
            f"Average Speed: {speed_avg:.2f}\n"
        )

        prompt = summary_text + '\n\n' + 'Please explain the data from Endurance, Physical Cabability, and Movement Efficiency three aspects.'
        st.session_state.messages.append({"role": "user", "content": prompt})
        process_message("Summarize Data")

    
    # Use a unique key for the chat input
    rehab_question = st.chat_input("Ask me your rehab question!", key="rehab_question")
    if rehab_question:
        st.session_state.messages.append({"role": "user", "content": rehab_question})
        process_message(rehab_question)
            


if __name__ == '__main__':
    if page == "Real-time Visualization":
        display_real_time_plot()
    elif page == "Historical Record":
        data, connected = fetch_data()  # Fetch all the data
        if connected and not data.empty:
            data_segments = segment_data_by_time_difference(data)
            if data_segments:
                display_historical_data()
                chatbot(data_segments)
            else:
                st.write("No data segments found.")
        else:
            st.write("Unable to connect to data source or no data available.")

