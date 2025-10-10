from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries
from gluonts.dataset.pandas import PandasDataset
from gluonts.dataset.split import split
from gluonts.torch import DeepAREstimator
from sklearn.linear_model import LinearRegression
from smolagents import tool
from sys import modules
from yfinance import Ticker

from .utils import get_tool_names

""" Author: Johnathan Kelsey
Mission: Analyze stock performance, historical growth, and future potential.
Models Used:
    DeepAR (AutoRegressive Integrated Moving Average) - for forecasting future price trends.
    Linear Regression - to identify long-term directional growth.
    SMA Indicators - for short-term trend momentum.
Tools & Libraries:
    yfinance (to fetch live and historical data)
    pandas, numpy (data manipulation)
Techniques:
    Time-series analysis, moving average convergence, and regression fitting to detect trend reversals and growth signals.
Output: Performance Score (0-1 scale)
"""

# Hyperparameters
REGRESSION_WEIGHT = 1.0
VALUE_WEIGHT = 1.0

def ticker_history(ticker_symbol, period):
    ticker = Ticker(ticker_symbol.upper())
    return ticker.history(period)

def calculate_linear_regression_scores(history):
	period_coefficients = []
	for period in history:
		x = period[["Open"]]
		y = period["Close"]

		model = LinearRegression()
		model.fit(x, y)

		period_coefficients.append(model.coef_.item())
	return sum(period_coefficients) / len(history)

def calculate_sma_scores(api_key, instrument):
    tech_indicators = TechIndicators(key=api_key, output_format="pandas", indexing_type="date")
    sma_data, _ = tech_indicators.get_sma(instrument)
    sma_data = sma_data["SMA"]

    # get ceoeficient of SMA line from 10, 20, and 30 days prior weighted by duration
    weighted_sma = 0
    for period in range(3):
        weighted_sma += (3 - period) * (sma_data.iloc[(period + 1) * 10] - sma_data.iloc[0]) / -((period + 1) * 10)
    average_sma = weighted_sma / 6
    return average_sma.item()

def calculate_armia_score(api_key, instrument):
    time_series = TimeSeries(key=api_key, output_format="pandas", indexing_type="date")
    intra_data, _ = time_series.get_intraday(instrument, interval="60min", outputsize="full")
    closing_data = intra_data[["4. close"]][::-16].rename(columns={"4. close": "price"})

    # Fill in missing data from market closures (ie. weekends)
    closing_data = closing_data.sort_index().asfreq(freq='1D')
    closing_data["price"] = closing_data["price"].ffill()

    dataset = PandasDataset(closing_data, target="price", freq="D")
    training_data, test_gen = split(dataset, offset=-10)
    test_data = test_gen.generate_instances(prediction_length=10)

    model = DeepAREstimator(
        prediction_length=10, freq="D", trainer_kwargs={"max_epochs": 5}
    ).train(training_data)

    forecasts = list(model.predict(test_data.input))
    expected_price = forecasts[0].quantile(q="p1")[-1].item()
    actual_price = closing_data.iloc[-1].item()
    return min(max((expected_price - actual_price) / 100, 0), 1)

@tool
def calculate_performance_score(alpha_api_key:str, instrument:str) -> float:
    """Calculate a performance score based on the model prediction of future financial instrument movement.
    
    Args:
        alpha_api_key (str): Alpha Vantage API key used to pull SMA and timeseries data.
        instrument (str): The financial instrument of interest.
    
    Returns:
        Float: A performance score between 0 and 1 with 1 being the most performant.
    """
    history = [ticker_history(instrument, period) for period in ["1y", "3y", "5y"]]
    combined_regression_score = calculate_linear_regression_scores(history)
    combined_sma_score = calculate_sma_scores(alpha_api_key, instrument)
    arima_score = calculate_armia_score(alpha_api_key, instrument)
    value_score = arima_score * combined_sma_score

    return (value_score * VALUE_WEIGHT + combined_regression_score * REGRESSION_WEIGHT) / (VALUE_WEIGHT + REGRESSION_WEIGHT)

# Map tools for easy export
self = modules[__name__]
self.__dict__["tools"] = [self.__dict__[tool_name] for tool_name in list(get_tool_names(self))]