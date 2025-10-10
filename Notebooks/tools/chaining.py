from bs4 import BeautifulSoup
from requests import get
from smolagents import tool
from sys import modules
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


# @tool
# def classify():
#     bert_df = pd.DataFrame(pipe(article))
#     sentiment = bert_df.label.value_counts().nlargest(1).index[0]
#     if sentiment == "positive":
#         return 1
#     if sentiment == "neutral":
#         return 0
#     return -1

# @tool
# def extract():
#     pass

# @tool
# def summarize():
#     pass

# Map tools for easy export
self = modules[__name__]
self.__dict__["tools"] = [self.__dict__[tool_name] for tool_name in list(get_tool_names(self))]