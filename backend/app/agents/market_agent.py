from groq import Groq
from tavily import TavilyClient
from app.agents.state import AgentState
import os
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("########################################################################"))
tavily_client = TavilyClient(api_key=os.getenv("##################################################"))

def search_web(query: str) -> str:
    print(f"  Searching: {query}")
    results = tavily_client.search(
        query=query,
        max_results=5
    )
    output = ""
    for r in results["results"]:
        output += f"Title: {r['title']}\n"
        output += f"Content: {r['content']}\n\n"
    return output

def market_research_node(state: AgentState) -> AgentState:
    """
    Node 1 - Search the web for market data and competitor information.
    """
    company = state["company"]
    print(f"\n Market Agent: Searching {company}....")

    try:
        market_data = search_web(f"{company} market size industry growth 2024")
        state["market_data"] = market_data
        state["status"] = "Market_done"
        print("Market Agent: Market data collected.")
    except Exception as e:
        state["status"] = "Market_error"
        state["error"] = str(e)
        
    return state

def competitor_search_node(state: AgentState) -> AgentState:
    """
    Node 2 - Search the web for competitor information.
    """
    company = state["company"]
    print(f"\n Competitor Agent: Searching competitors of {company}....")

    try:
        competitor_data = search_web(f"{company} top competitors alternatives 2024")
        state["competitor_data"] = competitor_data
        state["status"] = "Competitor_done"
        print("Competitor Agent: Competitor data collected.")
    except Exception as e:
        state["status"] = "Competitor_error"
        state["error"] = str(e)
        
    return state

def synthesizer_node(state: AgentState) -> AgentState:
    """
    Node 3 - Synthesize the collected data into a final report.
    """

    company = state["company"]
    print(f"\n Synthesizer Agent: Synthesizing report for {company}")

    prompt = f""" You Are a Senior Market Research Analyst.
      Write a professional market research report for {company} based on the following data:
      
      Market Data: {state.get('market_data', 'No market data available')}

      Competitor Data: {state.get('competitor_data', 'No competitor data available')}

      The report should include:
      
      1. Executive Summary
      2. Market Overview
      3. Top Competitors
      4. opportunities and Threats

      Write in a clear and concise manner, suitable for business stakeholders.
      """
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            messages=[
                {
                "role": "system", "content": "You are a senior market research analyst."
                },
               {
                "role": "user", "content": prompt
                }
                      ]
        )

        state["final_report"] = response.choices[0].message.content
        state["status"] = "complete"
        print("Synthesizer Agent: Report Completed.")

    except Exception as e:
        state["status"] = "Report_error"
        state["error"] = str(e)

    return state