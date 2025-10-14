import pandas as pd

from bs4 import BeautifulSoup
from transformers import pipeline
from requests import get
from smolagents import tool
from sys import modules
from textwrap import dedent
from yfinance import Search

from .utils import get_tool_names

""" Author: Johnathan Kelsey
Mission: Offer multiple tools to demonstrate prompt chaining
Output: Tool Dependent
"""

@tool
def retrieve_article_links(instrument:str) -> list[str]:
    """Perfomrs a quick search on the financial instrument provided and returns a list of URLs to links about the instrument.

    Args:
        instrument (string): The financial insturment in question.
        
    Returns:
        List(String): A list of URLs linking to articles about the financial instrument.
    """
    search = Search(instrument)
    urls = set()
    for article in search.news:
        urls.add(article["link"])
    return list(urls)

@tool
def preprocess(urls:list[str]) -> list[str]:
    """Uses a list of URLs to fetch news article data and returns a list of all articles found.

    Args:
        urls (list[string]): The list of article links.
        
    Returns:
        List(String): A list of articles.
    """
    full_articles = []
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0"
    }

    for url in urls:
        response = get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        parts = soup.find_all("p", class_="yf-1090901")
        full_article = [part.get_text() for part in parts]
        full_articles.append(full_article)

    return full_articles


@tool
def classify(articles: list[str]) -> list[int]:
    """Classify the sentiment of each article using BERT.

    Args:
        articles (list[str]): A list of articles to clasify.

    Returns:
        List(Integer): A list of integers indicating the sentiment of each article.
    """
    pipe = pipeline("text-classification", model="ProsusAI/finbert", max_length=512, truncation=True)

    sentiment_scores = []
    for article in articles:
        bert_df = pd.DataFrame(pipe(article))
        sentiment = bert_df.label.value_counts().nlargest(1).index[0]
        if sentiment == "positive":
            sentiment_scores.append(1)
        elif sentiment == "neutral":
            sentiment_scores.append(0)
        else:
            sentiment_scores.append(-1)

    return sentiment_scores
    

@tool
def extract(sentiment_scores: list[int]) -> dict:
    """Calculate a set of statistics based on the provided sentiment scores.

    Args:
        sentiment_scores (list[int]): A list of sentiment scores.

    Returns:
        Dictionary: A dictionary of specific statistics
    """
    return {
        "qty": len(sentiment_scores),
        "pos": sentiment_scores.count(1),
        "tral": sentiment_scores.count(0),
        "neg": sentiment_scores.count(-1),
    }

@tool
def summarize(stats:dict) -> str:
    """Summarize the statistics provided

    Args:
        stats (dict): A dictionary of statistics

    Returns:
        String: The final output string summarizing the statistics
    """
    qty, pos, tral, neg = stats.values()
    score = (pos - neg) / qty
    if score < 0:
        sentiment = "strongly " if score < -0.5 else "slightly "
        sentiment += "negative"
    elif score > 0:
        sentiment = "strongly " if score > 0.5 else "slightly "
        sentiment += "positive"
    else:
        sentiment = "neutral"

    return dedent(f"""
                  Of the {qty} articles reviwed, {pos / qty}% were positive, {neg / qty}% were negative, and {tral / qty}% were neutral.
                  The overall sentiment score as calculated by reviewing these articles is {score}. This indicates that the overall sentiment
                  about this financial instrument is {sentiment}.
                  """)

# Map tools for easy export
self = modules[__name__]
self.__dict__["tools"] = [self.__dict__[tool_name] for tool_name in list(get_tool_names(self))]