import pandas as pd

from bokeh.plotting import figure
from typing import Optional
from datetime import timedelta



def plot_candles (df: pd.DataFrame, 
                  window_seconds: Optional[int] = 60,
                  title: Optional[str] = '',
                  ) -> 'figure':
    """
    Generate a candlestick chart using Bokeh to visualize OHLC data with streamlit.
    The chart displays the open, high, low, and close prices of a stock over time.

    Args:
        df (pd.DataFrame): DataFrame containing OHLC data with 'timestamp', 'open', 'high', 'low', 'close' columns.
        window_seconds (int, optional): Time window in seconds for the x-axis. Defaults to 60.
        title (str, optional): Title of the chart. Defaults to ''.

    Returns:
        Figure: Bokeh figure object representing the candlestick chart.
    """
    
    # Prepare data
    # Parse the timestamp column and set it as the index
    df = df.copy()
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    inc = df.close > df.open
    dec = df.open > df.close
    
    
    w = 1000 * window_seconds / 2 # width of the candles in ms
    
    TOOLS = 'pan,wheel_zoom,box_zoom,reset,save'
    
    x_max = df['date'].max() + timedelta(minutes=5)
    x_min = df['date'].min() - timedelta(minutes=5) 
    
    # Create a Bokeh figure
    p = figure(
        x_axis_type="datetime",
        tools=TOOLS,
        width=1000, 
        title=title,
        x_range=(x_min, x_max),
    )
    p.grid.grid_line_alpha = 0.3
    
    # Plot the high-low segments
    p.segment (df.date, df.high, df.date, df.low, color="black")
    
    # Plot the candles
    p.vbar(df.date[inc], w, df.open[inc], df.close[inc], fill_color="#70bd40", line_color="black", width=3)
    p.vbar(df.date[dec], w, df.open[dec], df.close[dec], fill_color="#F2583E", line_color="black", width=3)
    
    return p