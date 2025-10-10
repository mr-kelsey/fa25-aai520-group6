import pandas as pd

from bs4 import BeautifulSoup
from datetime import date, timedelta
from requests import get
from smolagents import tool
from sys import modules
from textwrap import dedent
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .utils import get_tool_names
from .errors import NewsResponseError, TimeFrameError, YahooResponseError

""" Author: Johnathan Kelsey
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

# Hyperparameters
VADER_WEIGHT = 1.0
BERT_WEIGHT = 0.2

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

def call_news_api(api_key, query, timeframe):
    try:
        from_date = calculate_from_date(timeframe)
    except ValueError:
        raise TimeFrameError
    url = ("https://newsapi.org/v2/everything?"
        f"q={query}&"
        f"from={from_date}&"
        "language=en&"
        "sortBy=relevancy&"
        f"apiKey={api_key}")
    response = get(url)
    if response.status_code != 200:
        raise NewsResponseError
    top_25 = response.json()["articles"][:25]

    news_df = pd.DataFrame(columns=["title", "description", "url"])
    for article in top_25:
        news_df.loc[len(news_df)] = [article["title"], article["description"], article["url"]]
    return news_df

def call_yfinance_api():
    # Optional addition - Use Search feature for additional News Urls to boost sentiment analysis
    # This one would be very easy to implement with the current workflow
    pass

def call_edgar_api():
    # Optional addition - pull up most recent filing and analyze for sentiment as well
    pass

def calculate_VADER_score(sentence):
    analyzer = SentimentIntensityAnalyzer()
    polarity_scores = analyzer.polarity_scores(sentence)
    compound_score = polarity_scores["compound"]
    if compound_score >= 0.5:
        return 1
    if compound_score > -0.5:
        return 0
    return -1

def parse_yahoo_finance(url, headers):
    response = get(url, headers=headers)
    if response.status_code != 200:
        raise YahooResponseError
    soup = BeautifulSoup(response.text, "html.parser")

    parts = soup.find_all("p", class_="yf-1090901")
    full_article = [part.get_text() for part in parts]
    return full_article

def fetch_article(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0"
    }

    # Seperate parser required for every host - TODO: add more parsers
    if "finance.yahoo.com" in url:
        return parse_yahoo_finance(url, headers)
    return None

def calculate_BERT_score(pipe, article):
    bert_df = pd.DataFrame(pipe(article))
    sentiment = bert_df.label.value_counts().nlargest(1).index[0]
    if sentiment == "positive":
        return 1
    if sentiment == "neutral":
        return 0
    return -1

def calculate_sentiment_scores(dataframe, pipe):
    vader_score = calculate_VADER_score(dataframe["description"])
    article = fetch_article(dataframe["url"])
    bert_score = calculate_BERT_score(pipe, article) if article else 0
    combined_score = (vader_score * VADER_WEIGHT + bert_score * BERT_WEIGHT) / (VADER_WEIGHT + BERT_WEIGHT)
    return combined_score

@tool
def calculate_sentiment_score(news_api_key:str, query:str, timeframe:str = "30d") -> float:
    """Calculate a sentiment score from news articles related to the financial instrument in question.

    Args:
        news_api_key (str): NewsAPI key used to pull articles from NewsAPI.
        query (str): The keyword(s) used to query NewsAPI.
        timeframe (str): Time period to look back - default: 30 days.

    Returns:
        Float: The mean value of the sentiment classifications for all articles analyzed.
    """
    pipe = pipeline("text-classification", model="ProsusAI/finbert", max_length=512, truncation=True)
    try:
        news_df = call_news_api(news_api_key, query, timeframe)
        scores_df = news_df.apply(lambda df: calculate_sentiment_scores(df, pipe), axis=1)
        return (scores_df.sum() / len(scores_df)).item()

    except NewsResponseError:
        return dedent("""
                      NewsAPI returned an error.  The most likely cause is a bad API key.  You need to have a valid NewsAPI key stored as an environmental
                      variable.  Make sure to pass that variable to the tool so that it can be used in the get request.
                      """)
    except TimeFrameError:
        return dedent("""
                      There is an issue with your parameter `timeframe`. It must be in the format `10d` where `10` is the quantity and `d` is the period.
                      In this case, the `d` would represent days and the `10` would be the integer ten.  Thus, this would pull ten days worth of history.
                      Days, Months, and Years are supported.  Make sure not to add any whitespace when defining the parameter.
                      """)
    except YahooResponseError:
        return dedent("""
                      Yahoo returned an error.  The most likely cause for this is rate limiting.  Give it a few seconds before you attempt the next yahoo call.
                      """)

# Map tools for easy export
self = modules[__name__]
self.__dict__["tools"] = [self.__dict__[tool_name] for tool_name in list(get_tool_names(self))]