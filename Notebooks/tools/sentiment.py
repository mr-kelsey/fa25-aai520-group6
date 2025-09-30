from datetime import date, timedelta
from pandas import DataFrame
from requests import get
from smolagents import tool
from sys import modules
from textwrap import dedent

from .utils import get_tool_names

""" Assigned: J
Mission: Gauge market mood through news and media sentiment.
Models Used:
    FinBERT - transformer-based model fine-tuned for finance text sentiment.
    VADER Sentiment Analyzer - for quick polarity scoring.
Tools & Libraries:
    NewsAPI (to pull financial articles)
    BeautifulSoup (to parse news content)
    transformers (for FinBERT model)
Techniques:
    Text extraction, sentiment polarity scoring, and aggregation of scores from -1 (bearish) to +1 (bullish).
Output: Sentiment Score (-1 to +1)
"""

def calculate_from_date(timeframe):
    current_date = date.today()
    quantity, period = timeframe[:-1], timeframe[-1:]
    try:
        quantity = int(quantity)
    except ValueError:
        raise
    if period.upper() == "D":
        return current_date - timedelta(days=quantity)
    elif period.upper() == "M":
        return current_date - timedelta(months=quantity)
    elif period.upper() == "Y":
        return current_date - timedelta(years=quantity)
    else:
        raise ValueError

def call_news_api(query, timeframe, api_key):
    try:
        from_date = calculate_from_date(timeframe)
    except ValueError:
        raise
    url = ("https://newsapi.org/v2/everything?"
        f"q={query}&"
        f"from={from_date}&"
        "language=en&"
        "sortBy=relevancy&"
        f"apiKey={api_key}")
    response = get(url)
    if response.status_code != 200:
        raise ConnectionError
    first_ten_articles = response.json()["articles"][:10]

    news_df = DataFrame(columns=["title", "description", "url"])
    for article in first_ten_articles:
        news_df.loc[len(news_df)] = [article["title"], article["description"], article["url"]]
    return news_df

def call_yfinance_api():
    # Optional addition - Use Search feature for additional News Urls to boost sentiment analysis
    pass

def call_edgar_appi():
    # Optional addition - pull up most recent filing and analyze for sentiment as well
    pass

@tool
def calculate_sentiment_score(query:str, api_key:str) -> float:
    """Calculate a sentiment score from news articles related to the financial instrument in question.

    Args:
        query (str): The keyword(s) used to query NewsAPI.
        api_key (str): NewsAPI key used to pulls articles from NewsAPI.

    Returns:
        Float: The mean value of the sentiment classifications for all articles analyzed.
    """
    try:
        pass
    except ValueError:
        return dedent("""
                      There is an issue with your parameter `timeframe`. It must be in the format `10d` where `10` is the quantity and `d` is the period.
                      In this case, the `d` would represent days and the `10` would be the integer ten.  Thus, this would pull ten days worth of history.
                      Days, Months, and Years are supported.  Make sure not to add any whitespace when defining the parameter.
                      """)
    except ConnectionError:
        return dedent("""
                      Bad connection.  Perhaps missing api key?
                      """)
    return 10.0 # TODO: calculate dynamically

# Map tools for easy export
self = modules[__name__]
self.__dict__["tools"] = [self.__dict__[tool_name] for tool_name in list(get_tool_names(self))]