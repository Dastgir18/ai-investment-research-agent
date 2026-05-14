from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.market_agent import market_research_node, competitor_search_node, synthesizer_node


def build_pipeline():
  """
  Builds the agent pipline graph.

  Flow:
  market_research -> competitor_research -> synthesizer -> END
    """

  graph = StateGraph(AgentState)

  #Add all agent nodes to the graph
  graph.add_node("market_research",market_research_node)
  graph.add_node("competitor_research", competitor_search_node)
  graph.add_node("synthesizer", synthesizer_node)

  #Define the flow between nodes
  graph.set_entry_point("market_research")
  graph.add_edge("market_research", "competitor_research")
  graph.add_edge("competitor_research", "synthesizer")
  graph.add_edge("synthesizer", END)

  return graph.compile()


#Create a single instance of the pipeline to be used across requests
pipeline = build_pipeline()

def run_pipeline(company: str) -> dict:
  """
  Runs the agent pipeline for a given company and returns the final report or error message.
  """

  initial_state = AgentState(
    company=company,
    market_data=None,
    competitor_data=None,
    final_report=None,
    status="Started",
    error=None
  )


  
  print(f"\n Running pipeline for: {company}")
  print("="*50)

  result = pipeline.invoke(initial_state)

  #print("\nDEBUG RESULT:")
  #print(result)

  return {
  "company": result["company"],
  "report": result["final_report"],
  "status": result["status"],
  "error": result["error"]
}