from pandas import DataFrame
from sys import modules
from smolagents import tool
from yfinance import Ticker, Search

from .utils import get_tool_names

@tool
def ticker(ticker_symbol:str) -> Ticker:
    """Envoke Yahoo Finance API by ticker name.  Use this to fetch stock prices and company financials.
    The object returned by this tool can then be used by other tools that contain `ticker` in their name
    to extract more specific data about the stock.

    Args:
        ticker_symbol (str): 1 to 4 character string that represents the stock

    Returns:
        Ticker: A yfinance object that can be used to obtain more information about the stock
    """
    return Ticker(ticker_symbol.upper())

@tool
def ticker_financials(ticker:Ticker) -> DataFrame:
    """Extract company financials from Yahoo Finance ticker data

    Args:
        ticker (Ticker): Ticker object created by running ticker tool

    Returns:
        Dataframe: Financial data extracted from Ticker object
    """
    return ticker.financials

@tool
def ticker_history(ticker:Ticker, period:str = "1y") -> DataFrame:
    """Extract company history from Yahoo Finance ticker data

    Args:
        ticker (Ticker): Yahoo Finance ticker data.
        period (str, optional): The amount of history to look at - Defaults to 1y
            Options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

    Returns:
        Dataframe: Historical data extracted from Ticker object bound by the `period` timeframe
    """
    return ticker.history(period)

@tool
def ticker_sec_filings(ticker:Ticker) -> list[str]:
    """Extract Edgar URLs from Yahoo Finance ticker data

    Args:
        ticker (Ticker): Yahoo Finance ticker data

    Returns:
        List of Strings: Edgar URLs extracted from Ticker object
    """
    urls = set()
    for filing in ticker.sec_filings:
        urls.add(filing["edgarUrl"])
    return list(urls)

@tool
def search(ticker_symbol:str) -> Search:
    """Search Yahoo Finance for news articles by ticker name
    
    Args:
        ticker_symbol (str): 1 to 4 character string that represents the stock

    Returns:
        Search: An object containing news articles about the the stock
    """
    return Search(ticker_symbol.upper())

@tool
def search_news(search:Search) -> list[str]:
    """Extract news article URLs from Yahoo Finance search data

    Args:
        search (Search): Yahoo Finance search data

    Returns:
        List of Strings: News Article URLs extracted from Search object
    """
    urls = set()
    for article in search.news:
        urls.add(article["link"])
    
    return list(urls)


# Map tools for easy export
self = modules[__name__]
self.__dict__["tools"] = [self.__dict__[tool_name] for tool_name in list(get_tool_names(self))]