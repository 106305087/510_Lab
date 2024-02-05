"""
Change this to a world clock app
"""

import time

import streamlit as st

placeholder = st.empty()

cnt = 0
while True:
    with placeholder.container():
        placeholder.metric("Seconds since you arrived this page", cnt)
        cnt += 1
    time.sleep(1)