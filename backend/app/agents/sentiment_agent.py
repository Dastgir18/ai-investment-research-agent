from groq import Groq
from tavily import TavilyClient
from app.agents.state import AgentState
import os
import json
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("########################################################################"))
tavily_client = TavilyClient(api_key=os.getenv("##################################################"))


def fetch_news(company: str) -> list:
    """
    Searches for three types of news about the company.
    Returns a list of headlines and snippets.
    """
    print(f"  Fetching news for {company}...")

    all_news = []

    # Search 1 — general news
    results1 = tavily_client.search(
        query=f"{company} news today 2024",
        max_results=4
    )
    for r in results1["results"]:
        all_news.append(r["title"] + ". " + r["content"][:200])

    # Search 2 — financial news
    results2 = tavily_client.search(
        query=f"{company} financial news earnings 2024",
        max_results=3
    )
    for r in results2["results"]:
        all_news.append(r["title"] + ". " + r["content"][:200])

    # Search 3 — negative news
    results3 = tavily_client.search(
        query=f"{company} problems issues controversy 2024",
        max_results=3
    )
    for r in results3["results"]:
        all_news.append(r["title"] + ". " + r["content"][:200])

    print(f"  Fetched {len(all_news)} news items.")
    return all_news


def score_single_news(headline: str, company: str) -> float:
    """
    Sends one headline to Groq and gets a sentiment score.
    Returns a float between -1.0 and +1.0.

    -1.0 = very negative
     0.0 = neutral
    +1.0 = very positive
    """
    prompt = f"""
You are a financial sentiment analyst.
Score the sentiment of this news about {company}.

News: {headline}

Return ONLY a JSON object like this:
{{"score": 0.7, "reason": "one sentence explanation"}}

Rules:
- score must be between -1.0 and 1.0
- -1.0 = extremely negative
-  0.0 = neutral
- +1.0 = extremely positive
- Return ONLY the JSON. No extra text.
"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=100,
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial sentiment analyst. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw = response.choices[0].message.content.strip()

        # Clean markdown if present
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        data = json.loads(raw)
        score = float(data["score"])

        # Clamp between -1 and 1
        score = max(-1.0, min(1.0, score))
        return score

    except Exception:
        # If scoring fails return neutral
        return 0.0


def news_fetcher_node(state: AgentState) -> AgentState:
    """
    Node 1 — fetches news headlines about the company.
    Writes to state["raw_news"].
    """
    company = state["company"]
    print(f"\n News Fetcher: collecting news for {company}...")

    try:
        news_list = fetch_news(company)
        state["raw_news"] = news_list
        print(f"  Collected {len(news_list)} news items.")
    except Exception as e:
        state["error"] = str(e)
        state["status"] = "error"
        print(f"  Error: {e}")

    return state


def sentiment_scorer_node(state: AgentState) -> AgentState:
    """
    Node 2 — scores each headline individually.
    Writes list of scores to state["sentiment_scores"].
    """
    company = state["company"]
    news_list = state.get("raw_news", [])

    print(f"\n Sentiment Scorer: scoring {len(news_list)} headlines...")

    scores = []

    for i, headline in enumerate(news_list):
        score = score_single_news(headline, company)
        scores.append(score)
        print(f"  [{i+1}/{len(news_list)}] Score: {score:+.2f}")

    state["sentiment_scores"] = scores
    print(f"  All headlines scored.")

    return state


def sentiment_aggregator_node(state: AgentState) -> AgentState:
    """
    Node 3 — aggregates all scores into one final result.
    Writes structured dict to state["sentiment_result"].
    """
    company = state["company"]
    scores = state.get("sentiment_scores", [])
    news_list = state.get("raw_news", [])

    print(f"\n Sentiment Aggregator: building final result...")

    if not scores:
        state["sentiment_result"] = {
            "overall_score": 0.0,
            "label": "Neutral",
            "summary": "No news data available",
            "top_positive": [],
            "top_negative": [],
            "recommendation": "Insufficient data"
        }
        state["status"] = "complete"
        return state

    # Calculate average score
    overall_score = sum(scores) / len(scores)
    overall_score = round(overall_score, 2)

    # Determine label
    if overall_score >= 0.3:
        label = "Positive"
    elif overall_score <= -0.3:
        label = "Negative"
    else:
        label = "Neutral"

    # Find top positive and negative headlines
    news_with_scores = list(zip(scores, news_list))
    news_with_scores.sort(key=lambda x: x[0], reverse=True)

    top_positive = [
        {"headline": news[:100], "score": score}
        for score, news in news_with_scores[:3]
        if score > 0
    ]

    top_negative = [
        {"headline": news[:100], "score": score}
        for score, news in reversed(news_with_scores)
        if score < 0
    ][:3]

    # Investment recommendation based on sentiment
    if overall_score >= 0.5:
        recommendation = "Strong positive sentiment — supports investment"
    elif overall_score >= 0.2:
        recommendation = "Mildly positive sentiment — cautiously favorable"
    elif overall_score >= -0.2:
        recommendation = "Neutral sentiment — no strong signal"
    elif overall_score >= -0.5:
        recommendation = "Mildly negative sentiment — exercise caution"
    else:
        recommendation = "Strong negative sentiment — avoid investment"

    # Ask Groq to write a summary
    summary_prompt = f"""
You are a financial analyst.
Write 2-3 sentences summarizing the overall news sentiment 
for {company}.

Overall sentiment score: {overall_score} ({label})
Number of news items analyzed: {len(scores)}
Positive headlines: {len(top_positive)}
Negative headlines: {len(top_negative)}

Write a concise professional summary.
"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=150,
            messages=[
                {
                    "role": "user",
                    "content": summary_prompt
                }
            ]
        )
        summary = response.choices[0].message.content.strip()
    except Exception:
        summary = f"Overall sentiment for {company} is {label} with a score of {overall_score}."

    state["sentiment_result"] = {
        "overall_score": overall_score,
        "label": label,
        "summary": summary,
        "total_news_analyzed": len(scores),
        "top_positive": top_positive,
        "top_negative": top_negative,
        "recommendation": recommendation
    }

    state["status"] = "complete"
    print(f"  Sentiment: {label} ({overall_score:+.2f})")
    print(f"  Recommendation: {recommendation}")

    return state