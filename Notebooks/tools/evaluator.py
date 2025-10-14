from smolagents import tool
from sys import modules
from textwrap import dedent

from .utils import get_tool_names
from .errors import RecommendationError

""" Author: Tadhbir Singh
Mission: Audit, validate, and optimize Commander's final decision.
Models Used:
    XGBoost - to re-check classification patterns.
    Random Forest - to cross-validate ensemble output.
Tools & Libraries:
    scikit-learn, FIASS vector DB, pandas
Techniques:
    Evaluator-Optimizer Pattern:
    Step 1: Re-audit every input-output pair.
    Step 2: Optimize final confidence level.
    Step 3: Log discrepancies for retraining.
Output: Final Approved Verdict
"""

def evaluate(performance_score, risk_score, sentiment_score, impact_score, recommendation):
    if recommendation == "BUY":
        if performance_score < 0.15:
            # Performance is too low
            return "FAIL"
        if risk_score > 0.7:
            # Risk is too high
            return "FAIL"
        return "PASS"
    
    elif recommendation == "HOLD":
        if sentiment_score < -0.8:
            # Too negative a sentiment
            return "FAIL"
        return "PASS"
    
    elif recommendation == "AVOID":
        if impact_score >= 0.95 and sentiment_score >= 0.5:
            # Too important to pass up
            return "FAIL"
        return "PASS"
    
    else:
        raise RecommendationError

@tool
def check_logic(performance_score:float, risk_score:float, sentiment_score:float, impact_score:float, recommendation:str) -> str:
    """Review commander logic and determine if the logic is sound.

    Args:
        performance_score (float): The performance score as calculated by Performance.
        risk_score (float): The risk score as calculated by Risk.
        sentiment_score (float): The sentiment score as calculated by Sentiment.
        impact_score (float): The impact score as calculated by Impact.
        recommendation (str): The recommendation as determined by Commander.

    Returns:
        String: "PASS" or "FAIL" based on the soundness of the provided logic.
    """
    try:
        return evaluate(performance_score, risk_score, sentiment_score, impact_score, recommendation)
    except RecommendationError:
        return dedent("""
                      There was an error processing your logic.  You need to make sure that your recommendation is either "BUY" or
                      "HOLD" or "AVOID".  It cannot be any other value.
                      """)
        

# Map tools for easy export
self = modules[__name__]
self.__dict__["tools"] = [self.__dict__[tool_name] for tool_name in list(get_tool_names(self))]