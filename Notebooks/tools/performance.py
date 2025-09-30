from dotenv import dotenv_values
from pandas import DataFrame
from pathlib import Path
from requests import get
from smolagents import tool
from sys import modules
from textwrap import dedent
from yfinance import Ticker

from .utils import get_tool_names

""" Assigned: J
Mission: Analyze stock performance, historical growth, and future potential.
Models Used:
    ARIMA (AutoRegressive Integrated Moving Average) - for forecasting future price trends.
    Linear Regression - to identify long-term directional growth.
    SMA/EMA Indicators - for short-term trend momentum.
Tools & Libraries:
    yfinance (to fetch live and historical data)
    pandas, numpy (data manipulation)
    matplotlib (data visualization)
Techniques:
    Time-series analysis, moving average convergence, and regression fitting to detect trend reversals and growth signals.
Output: Performance Score (0-1 scale)
"""

def ticker_history(ticker_symbol, period="1y"):
    ticker = Ticker(ticker_symbol.upper())
    return ticker.history(period)

def call_alpha_vantage_api():
    # Optional addtion - Pull timeseries data from alpha_vantage
    pass

@tool
def calculate_performance_score(instrument:str) -> float:
    """Calculate a performance score based on the model prediction of future financial instrument movement.
    
    Args:
        instrument (str): The financial instrument of interest.
    
    Returns:
        Float: A performance score between 0 and 10 with 10 being the most performant.
    """
    return 10.0 # TODO: Calculate this dynamically

# Map tools for easy export
self = modules[__name__]
self.__dict__["tools"] = [self.__dict__[tool_name] for tool_name in list(get_tool_names(self))]