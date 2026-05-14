from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.investment_agent import financial_data_node, risk_analysis_node, stock_news_node, investment_memo_node


def build_investment_pipeline():
    """
    Builds the investment research pipline graph.

    Flow:
    financial_data -> risk_analysis -> stock_news -> investment_memo -> END
    """

    graph = StateGraph(AgentState)

    #Add all agent nodes to the graph
    graph.add_node("financial_data", financial_data_node)
    graph.add_node("risk_analysis", risk_analysis_node)
    graph.add_node("stock_news", stock_news_node)
    graph.add_node("investment_memo", investment_memo_node)

    #Define the flow between nodes
    graph.set_entry_point("financial_data")
    graph.add_edge("financial_data", "risk_analysis")
    graph.add_edge("risk_analysis", "stock_news")
    graph.add_edge("stock_news", "investment_memo")
    graph.add_edge("investment_memo", END)

    return graph.compile()

#Single instance of the investment pipeline to be used across requests
investment_pipeline = build_investment_pipeline()

def run_investment_pipeline(company: str) -> dict:
    """
    Runs the investment research pipeline for a given company and returns the final report or error message.
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
        status="Started",
        error=None
    )

    print(f"\n Investment Pipeline Started for: {company}")
    print("="*50)

    result = investment_pipeline.invoke(initial_state)

    #print("\nDEBUG RESULT:")
    #print(result)

    return {
        "company": result["company"],
        "investment_memo": result["investment_memo"],
        "status": result["status"],
        "error": result["error"]
    }