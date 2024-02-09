from datetime import datetime
import streamlit as st
import pytz
import time

if 'page' not in st.session_state:
    st.session_state.page = 'world_clock'

# Define function for setting the page state
def set_page(page):
    st.session_state.page = page

# Sidebar for page navigation
st.sidebar.title("Navigation")
st.sidebar.button("World Clock", on_click=set_page, args=('world_clock',))
st.sidebar.button("UNIX Timestamp Converter", on_click=set_page, args=('timestamp_converter',))

# Function to display the world clock
def world_clock():
    st.title('World Clock')

    # List of time zones
    time_zones = list(pytz.all_timezones)

    # Multi-select dropdown for time zones
    selected_zones = st.multiselect("Choose up to 4 time zones", time_zones, default=["UTC"])

    # Placeholder for clocks
    clocks_container = st.empty()
    while True:
        with clocks_container.container():
            st.write("Current UNIX Timestamp:", int(time.time()))
            # Display clocks
            for zone in selected_zones:
                tz = pytz.timezone(zone)
                time_now = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
                st.metric(zone, time_now)
        time.sleep(1)

# Function to convert UNIX timestamp to human-readable time
def timestamp_converter():
    st.title('UNIX Timestamp Converter')

    # Input for UNIX timestamp
    unix_timestamp = st.number_input("Enter UNIX Timestamp", step=1, format="%d")

    # Timezone selection for the conversion
    timezone_selection = st.selectbox("Select Time Zone for Conversion", pytz.all_timezones, index=pytz.all_timezones.index("UTC"))

    # Convert and display
    if st.button("Convert"):
        tz = pytz.timezone(timezone_selection)
        human_time = datetime.fromtimestamp(unix_timestamp, tz).strftime('%Y-%m-%d %H:%M:%S')
        st.write("Human-readable Time:", human_time)

# Display the selected page
if st.session_state.page == 'world_clock':
    world_clock()
elif st.session_state.page == 'timestamp_converter':
    timestamp_converter()