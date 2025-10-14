from smolagents import tool
from sys import modules

from .utils import get_tool_names

""" Assigned: J
Mission: Synthesize all agent outputs and deliver final classification.
Models Used:
    Weighted Ensemble Formula
    Decision Tree Classifier
Techniques:
    Integrates agent outputs into one score using formula:
        Final_Score = (0.4*Performance) + (0.2*Risk) + (0.3*Sentiment) + (0.1*Impact)
    Classifies results into:
        Buy (score > 0.7)
        Hold (0.4-0.7)
        Avoid (< 0.4)
Output: Preliminary Verdict (Buy / Hold / Avoid)
"""

# Hyperparameters
PERFORMANCE_WEIGHT = 0.9
SENTIMENT_WEIGHT = 0.7
RISK_WEIGHT = 0.5
IMPACT_WEIGHT = 0.25
BUY_THRESHOLD = 0.55
HOLD_THRESHOLD = 0.5
assert BUY_THRESHOLD >= HOLD_THRESHOLD, "Buy threshold must be at least as large as hold threshold"

def calculate_final_score(performance_score, risk_score, sentiment_score, impact_score):
    return (performance_score * PERFORMANCE_WEIGHT) - (risk_score * RISK_WEIGHT) + (sentiment_score * SENTIMENT_WEIGHT) + (impact_score * IMPACT_WEIGHT)

# define tools here
@tool
def make_reccomendation(performance_score:float, risk_score:float, sentiment_score:float, impact_score:float) -> str:
    """ Dummy tool to show required format for tool use

    Args:
        performance_score (float): The performance score as calculated by Performance.
        risk_score (float): The risk score as calculated by Risk.
        sentiment_score (float): The sentiment score as calculated by Sentiment.
        impact_score (float): The impact score as calculated by Impact.
        
    Returns:
        String: One of three recommendations: "BUY", "HOLD", "AVOID"
    """
    final_score = calculate_final_score(performance_score, risk_score, sentiment_score, impact_score)

    if final_score > BUY_THRESHOLD:
        return "BUY"
    if final_score > HOLD_THRESHOLD:
        return "HOLD"
    return "AVOID"

# Map tools for easy export
self = modules[__name__]
self.__dict__["tools"] = [self.__dict__[tool_name] for tool_name in list(get_tool_names(self))]