from app.agents.sentiment_pipeline import run_sentiment_pipeline

if __name__ == "__main__":
    company = input("Enter a company name for sentiment analysis: ")
    result = run_sentiment_pipeline(company)
    
    if result["status"] == "complete":
        sentiment = result["sentiment"]

        print("\n")
        print("="*50)
        print("Sentiment Analysis Report")
        print("="*50)

        score = sentiment["overall_score"]
        label = sentiment["label"]


        #Visual  Score bar
        positive_bars = int((score + 1) / 2 * 20)  # Scale score to 0-20
        negative_bars = 20 - positive_bars
        bar = "█" * positive_bars + "░" * negative_bars

        print(f"\n Company: {result['comany']}")
        print(f"Overall Sentiment Score: {score :+.2f}")
        print(f"sentiment_label: {label}")
        print(f"Sentiment Bar: [{bar}]")
        print(f"\n Summary:")
        print(f" {sentiment['summary']}")
        print(f"\n Recommendation: {sentiment['recommendation']}")
        print(f"\n News analyzed: {sentiment['total_news_analyzed']}")

        if sentiment['top_positive']:
            print(f"\n Top Positive Headlines:")
            for item in sentiment['top_positive']:
                print(f"  +{item['score']:.2f} | {item['headline']}")

        if sentiment['top_negative']:
            print(f"\n Top Negative Headlines:")
            for item in sentiment['top_negative']:
                print(f"  {item['score']:.2f} | {item['headline']}")

        else:
            print("No news data available for sentiment analysis.")        
    
    