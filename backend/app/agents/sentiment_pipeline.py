from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.sentiment_agent import news_fetcher_node, sentiment_scorer_node, sentiment_aggregator_node

def build_sentiment_pipeline():
    """
    Sentiment pipeline flow:

    news_fetcher -> sentiment_scorer -> sentiment_aggregator -> END 
    """

    graph = StateGraph(AgentState)

    graph.add_node("news_fetcher", news_fetcher_node)
    graph.add_node("sentiment_scorer", sentiment_scorer_node)
    graph.add_node("sentiment_aggregator", sentiment_aggregator_node)

    graph.set_entry_point("news_fetcher")
    graph.add_edge("news_fetcher", "sentiment_scorer")
    graph.add_edge("sentiment_scorer", "sentiment_aggregator")
    graph.add_edge("sentiment_aggregator", END)

    return graph.compile()

sentiment_pipeline = build_sentiment_pipeline()

def run_sentiment_pipeline(company: str) -> dict:
    """
    Runs the sentiment analysis pipeline for a given company and returns the sentiment results or error message.
    """
    initial_state = AgentState(
        company=company,
        market_data=None,
        competitor_data=None,
        financial_data=None,
        risk_data=None,
        stock_news=None,
        final_report=None,
        investment_memo=None,
        raw_news=None,
        sentiment_scores=None,
        sentiment_result=None,
        status="Started",
        error=None
    )

    print(f"\n Sentiment Pipeline Started for: {company}")
    print("="*50)

    result = sentiment_pipeline.invoke(initial_state)

    return {
        "comany": company,
        "sentiment": result["sentiment_result"],
        "status": result["status"],
        "error": result["error"]

    }