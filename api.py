from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
import uvicorn
from utils import fetch_articles_fallback, analyze_sentiment, extract_topics, generate_summary, compare_sentiment, calculate_sentiment ,get_topic_overlap, final_sentiment

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the News Analysis API"}

@app.get("/news/{company_name}")
def get_news_articles(company_name: str) -> List[Dict[str, Any]]:
    """
    Fetch news articles for a given company and generate the summary of the articles
    """
    try:
        articles = fetch_articles_fallback(company_name,10)
        article_summary = generate_summary(articles)
        return article_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/sentiment")
def analyze_articles_sentiment(articles: List[Dict[str, Any]],company_name: str) -> Dict[str, Any]:
    """
        Function to analyze articles sentiment and extract topics from articles
        and also calculate the overall sentiments and other information.
    """
    try:
        results = []
        for article in articles:
            sentiment = analyze_sentiment(article['Summary'])
            topics = extract_topics(article['Summary'])
            article['Sentiment'] = sentiment
            article['Topics'] = topics
            
        
        # Comparative Sentiment report
        positive,negative,neutral = calculate_sentiment(articles) 
        comparative_sentiment_report = compare_sentiment(articles,company_name)
        topic_overlap = get_topic_overlap(articles)
        final_sentiment_report = final_sentiment(articles)

        for art in articles:
            if "URL" in art and "Content" in art:
                del art["URL"]
                del art["Content"]

        output = {"Company": company_name,
                "Articles": articles,
                "Comparative Sentiment Score": {
                "Sentiment Distribution": {
                    "Positive": positive,
                    "Negative": negative,
                    "Neutral": neutral
                },
                "Coverage Differences": comparative_sentiment_report["Coverage Differences"],
                "Topic Overlap": topic_overlap["Topic Overlap"],
                "Final Sentiment": final_sentiment_report
                }
            }

        return output

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For local testing
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)