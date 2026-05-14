from typing import TypedDict , Optional , List

class AgentState(TypedDict):
    #Input
    company: str

    #Market Agent Output
    market_data: Optional[str]
    competitor_data: Optional[str]

    #Investment Agent Output
    financial_data: Optional[str]
    risk_data: Optional[str]
    stock_news: Optional[str]

    #Final Report Output
    final_report: Optional[str]
    investment_memo: Optional[str]

    # Sentiment Agent Output
    raw_news: Optional[List[str]]
    sentiment_scores: Optional[List[float]]
    sentiment_result: Optional[dict]

    #Tracking
    status: str
    error: Optional[str]
      

