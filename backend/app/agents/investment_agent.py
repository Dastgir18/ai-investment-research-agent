from groq import Groq
from tavily import TavilyClient
from app.agents.state import AgentState
import os
import json
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("#########################################################"))
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

def financial_data_node(state: AgentState) -> AgentState:
    """
    Node 1 - Search the web for financial data and stock news.
    """
    company = state["company"]
    print(f"\n Financial Agent: Collecting financial data for {company}....")

    try:
        financial_data = search_web(f"{company} revenue profit earnings growth rate 2024 financials")
        state["financial_data"] = financial_data
        #state["status"] = "Financial_done"
        print("Financial Agent: Financial data collected.")
    except Exception as e:
        state["status"] = "Financial_error"
        state["error"] = str(e)
        
    return state


def risk_analysis_node(state: AgentState) -> AgentState:
    """
    Node 2 - Search the web for risk factors and challenges.
    """
    company = state["company"]
    print(f"\n Risk Agent: Collecting risk data for {company}....")

    try:
        risk_data = search_web(f"{company} risks challenges weaknesses 2024")
        state["risk_data"] = risk_data
        #state["status"] = "Risk_done"
        print("Risk Agent: Risk data collected.")
    except Exception as e:
        state["status"] = "Risk_error"
        state["error"] = str(e)
        
    return state

def stock_news_node(state: AgentState) -> AgentState:
    """
    Node 3 - Search the web for recent stock news and developments.
    """
    company = state["company"]
    print(f"\n Stock News Agent: Collecting stock news for {company}....")

    try:
        stock_news = search_web(f"{company} stock news developments 2024")
        state["stock_news"] = stock_news
        #state["status"] = "StockNews_done"
        print("Stock News Agent: Stock news collected.")
    except Exception as e:
        state["status"] = "StockNews_error"
        state["error"] = str(e)
        
    return state

def investment_memo_node(state: AgentState) -> AgentState:
    company = state["company"]
    print(f"\n Investment Memo Agent: Synthesizing investment memo for {company}")

    prompt = f"""
You are a senior investment analyst at a top hedge fund.
Analyze the following data about {company} and write
a professional investment memo.

FINANCIAL DATA:
{state.get("financial_data", "No data available")}

RISK FACTORS:
{state.get("risk_data", "No data available")}

RECENT NEWS:
{state.get("stock_news", "No data available")}

Return your analysis as a JSON object with exactly
these fields:

{{
    "executive_summary": "2-3 sentence overview",
    "bull_case": "3 strong reasons to invest",
    "bear_case": "3 strong reasons to avoid",
    "key_risks": "top 3 specific risks with explanation",
    "financial_highlights": "key numbers and metrics",
    "risk_score": 7,
    "recommendation": "Buy or Hold or Sell or Watch",
    "reasoning": "2-3 sentences explaining recommendation",
    "time_horizon": "Short term or Medium term or Long term"
}}

Return ONLY the JSON object. No extra text. No markdown.
"""

    raw = ""

    try:
        print(" Calling Groq API...")

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior investment analyst. Respond with valid JSON only. No markdown, no explanation, just the JSON object."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        print(" Groq API call successful.")
        raw = response.choices[0].message.content.strip()
        #print(f"\n RAW GROQ RESPONSE:\n{raw}\n")

        # Clean markdown if present
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        if raw.endswith("```"):
            raw = raw[:-3]

        memo = json.loads(raw.strip())
        state["investment_memo"] = memo
        state["status"] = "complete"
        print(" Investment Memo Agent: Memo completed.")

    except json.JSONDecodeError as e:
        print(f" JSON parse error: {e}")
        print(f" Raw text that failed: {raw}")
        state["investment_memo"] = {
            "raw": raw,
            "error": "Could not parse JSON"
        }
        state["status"] = "complete"

    except Exception as e:
        import traceback
        print(f" Full error traceback:")
        traceback.print_exc()
        state["error"] = str(e)
        state["status"] = "error"

    return state
    