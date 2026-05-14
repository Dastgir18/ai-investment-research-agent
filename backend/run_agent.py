from app.agents.pipeline import run_pipeline

if __name__ == "__main__":

  company = input("Enter a company name for market research: ")
  result = run_pipeline(company)

  if result["status"] == "complete":
    print(f"\n")
    print("=" * 50)
    #print(f"Final Report for {result['company']}:")
    print("Final Report:")
    print("=" * 50)
    print(result["report"])
  else:
    print(f"\n Error: {result['error']}")
