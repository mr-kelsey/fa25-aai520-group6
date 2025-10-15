from sys import modules
from smolagents import tool
from yfinance import download

from .utils import get_tool_names

""" Author: Tadhbir Singh
Mission: Measure risk, volatility, and downside probability.
Models Used:
    Monte Carlo Simulation - simulates potential price paths to estimate volatility.
    Sharpe Ratio - evaluates return vs. risk.
    Beta Coefficient - measures correlation with the broader market.
Tools & Libraries:
    numpy, scipy.stats, pandas
Techniques:
    Randomized forecasting, probability modeling, and portfolio variance estimation to flag high-risk assets.
Output: Risk Score (lower = safer)
"""

@tool
def calculate_risk(symbol:str) -> float:
    """Calculate a risk score based on downside deviation.

    Args:
        symbol (str): Financial instrument symbol in question.

    Returns:
        Float: The risk score.
    """
    data = download(symbol, period="1y", progress=False)
    data["Return"] = data["Close"].pct_change()
    downside = data[data["Return"] < 0]["Return"]
    risk_score = abs(downside.mean()) if not downside.empty else 0
    return min(round(risk_score.item(), 3), 1)

# Map tools for easy export
self = modules[__name__]
self.__dict__["tools"] = [self.__dict__[tool_name] for tool_name in list(get_tool_names(self))]