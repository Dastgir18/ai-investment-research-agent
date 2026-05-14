from app.agents.investment_pipeline import run_investment_pipeline

if __name__ == "__main__":
    company = input("Enter a company name for investment research: ")
    result = run_investment_pipeline(company)

    print("\n")
    print("=" * 50)
    print("Investment Memo:")
    print("=" * 50)

    if result["status"] == "complete":
        memo = result["investment_memo"]

        if memo is None:
            print("No memo generated.")
        elif "raw" in memo:
            # Raw text fallback
            print(memo["raw"])
        else:
            print(f"\n Company         : {result['company']}")
            print(f" Recommendation  : {memo.get('recommendation', 'N/A')}")
            print(f" Risk Score      : {memo.get('risk_score', 'N/A')}/10")
            print(f" Time Horizon    : {memo.get('time_horizon', 'N/A')}")

            print(f"\n Executive Summary:")
            print(f" {memo.get('executive_summary', 'N/A')}")

            print(f"\n Bull Case:")
            print(f" {memo.get('bull_case', 'N/A')}")

            print(f"\n Bear Case:")
            print(f" {memo.get('bear_case', 'N/A')}")

            print(f"\n Key Risks:")
            print(f" {memo.get('key_risks', 'N/A')}")

            print(f"\n Financial Highlights:")
            print(f" {memo.get('financial_highlights', 'N/A')}")

            print(f"\n Reasoning:")
            print(f" {memo.get('reasoning', 'N/A')}")

    else:
        print(f"Error: {result.get('error')}")