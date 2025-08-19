import streamlit as st
import pandas as pd
from loguru import logger
from time import sleep

from src.backend import get_features_from_the_store
from src.plot import plot_candles
from src.config import config

st.write("""
# OHLC features dashboard
""")

# add a selectbox to the sidebar to switch between the online store
# and the offline store
online_or_offline = st.sidebar.selectbox(
    'Select the store',
    ('offline', 'online')
)
with st.container():
    placeholder_chart = st.empty()

# Load the data from the feature store
data = get_features_from_the_store(online_or_offline)
logger.debug(f'Received {len(data)} rows of data from the feature store')
# logger.debug(data.head())

st.table(data.tail(10))  # Display the last 10 rows of the data


# Plot the data
st.write("## Features Data")

while True:
    # Load the data
    data = get_features_from_the_store(online_or_offline)
    logger.debug(f'Received {len(data)} rows of data from the Feature Store')

    # Refresh the chart
    with placeholder_chart:
        st.bokeh_chart(plot_candles(data))
        # st.bokeh_chart(plot_candles(data.tail(1440)))

    sleep(15)  # Refresh every 15 seconds
    if online_or_offline == 'offline':
        break

   


