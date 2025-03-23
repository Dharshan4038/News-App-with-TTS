import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict, Any
from newspaper import Article
import time
import json
from langchain_groq import ChatGroq
import ast
from collections import defaultdict
import os
from dotenv import load_dotenv



load_dotenv()

llm = ChatGroq(
        model = "llama-3.3-70b-versatile",
        api_key = os.getenv("GROQ_API_KEY")
    )


def fetch_news_articles(company_name: str, min_articles: int = 10) -> List[Dict[str, Any]]:
    API_KEY = os.getenv('GOOGLE_API_KEY')
    CX = os.getenv('GOOGLE_CX')

    max_attempts = 3
    search_url = "https://www.googleapis.com/customsearch/v1"
    collected_links = set()
    start = 1  

    for _ in range(max_attempts): 
        params = {
            "q": company_name + "Current News",
            "key": API_KEY,
            "cx": CX,
            "num": min(min_articles, 10),  # Max 10 per request
            "start": start
        }
        
        response = requests.get(search_url, params=params)
        
        if response.status_code == 200:
            results = response.json()
            new_links = {item["link"] for item in results.get("items", [])}

            # Filter out non-news sites
            new_links = {url for url in new_links if "tesla.com" not in url.lower()}
            collected_links.update(new_links)
        
        start += 10  # Move to the next page of results
        time.sleep(1)  # Avoid rate-limiting

        if len(collected_links) >= min_articles:
            break  # Stop early if we have enough links
    
    return list(collected_links)[:min_articles]

def extract_article_content(url: str) -> Dict[str, str]:
    retries = 3  # Number of retries for fetching the article
    for _ in range(retries):
        try:
            article = Article(url)
            article.download()
            article.parse()

            return {
                "Title": article.title,
                "URL": url,
                "Content": article.text
            }
        except Exception as e:
            time.sleep(2)  # Wait before retrying
    
    return {"Title": "Error", "URL": url, "Content": "Failed to fetch article"}

def fetch_articles_fallback(company_name: str, num_articles: int) -> List[Dict[str, Any]]:
    """Fetches and scrapes at least 10 unique news articles related to a company."""
    news_links = fetch_news_articles(company_name, min_articles=num_articles + 5)  # Fetch extra to ensure 10 valid ones
    print(f"Found {len(news_links)} URLs:", news_links)

    unique_articles = []
    seen_urls = set()
    
    for url in news_links:
        if url not in seen_urls:
            seen_urls.add(url)
            article = extract_article_content(url)
            # print(article)

            if article["Content"] and "Error" not in article["Title"]:
                unique_articles.append(article)
            
            if len(unique_articles) >= num_articles:
                break
        
        time.sleep(1)  # Avoid overloading server
    
    # If fewer than required articles are fetched, retry fetching more
    if len(unique_articles) < num_articles:
        print(f"Only {len(unique_articles)} articles fetched. Retrying for more...")
        extra_news_links = fetch_news_articles(company_name, num_results=(num_articles - len(unique_articles) + 5))
        
        for url in extra_news_links:
            if url not in seen_urls:
                seen_urls.add(url)
                article = extract_article_content(url)

                if article["Content"] and "Error" not in article["Title"]:
                    unique_articles.append(article)

                if len(unique_articles) >= num_articles:
                    break
            
            time.sleep(1)
    
    # print(f"Final count: {len(unique_articles)} articles.")
    return unique_articles




def generate_summary(articles):
    for art in articles:
        title = art['Title']
        content = art['Content'][:6000]
        summary_prompt = f"""I will give you the title and the content of the news article, 
                    I need you to generate the summary of the entire news article, remember it should explain every important points in the news, 
                    the summary should be in the word limit of 150-160 words, It should provide clear understanding about the news and 
                    return the summary alone, Remember do not provide any extra content. 
                    Here is the title: {title}\n\n content: {content}
                    - Return the summary of the article as a string.
                    """
        summary = llm.invoke(summary_prompt)
        art["Summary"] = summary.content

    return articles

def analyze_sentiment(content: str) -> str:
    sentiment_prompt = f"""I will give you the content of the news article 
                            I need you to understand the content of the news article
                            and Remember do not provide any extra content just return 
                            the sentiment of the news article with single word as either 'Positive', 'Negative' or 'Neutral'. 
                            Here is the content: {content}.
                        """

    sentiment = llm.invoke(sentiment_prompt)
    return sentiment.content

def extract_topics(content: str) -> List[str]:
    topics_prompt = f"""I will give you the content of the new article 
                        I need you to understand the content of the news article and identify the topics 
                        disscussed in the content and return all those topics as a list. 
                        Example: ["Electric Vehicles", "Stock Market", "Innovation"].
                        Remember the above given items are just for an example, I need you to identify the topics that are provided in the content that I give.
                        And also return only the list of topics, do not return any extra information.
                        Here is the content: {content}
                    """
    topics = llm.invoke(topics_prompt)
    topics = ast.literal_eval(topics.content)
    return topics

def calculate_sentiment(articles):
    negative = 0
    positive = 0
    neutral = 0
    for art in articles:
        if art['Sentiment'] == 'Positive':
            positive += 1
        elif art['Sentiment'] == 'Negative':
            negative += 1
        else:
            neutral += 1
    
    return positive,negative,neutral

def compare_sentiment(articles,company_name):
    summaries = []

    for art in articles:
        summaries.append(art['Summary'])
    
    
    prompt = f"""
    Given the following news articles summary about a company {company_name} , conduct a comparative sentiment analysis.
    I want you to througly analyze the all the articles summary before making a comparison, And I want you to provide 
    a comparative analysis of the sentiment coverage across the articles.

    Articles:
    {summaries}

    Based on the articles:
    - Identify key topics covered across multiple articles.
    - Compare **sentiment variations** on the same topic (e.g., positive vs. negative coverage).
    - Highlight the **impact** of different sentiment coverage on public perception.

    Provide your response in the following JSON format:
    {{
      "Coverage Differences": [
        {{
          "Comparison": "Article 1 highlights a positive business move by Apple, while Article 2 discusses regulatory challenges.",
          "Impact": "The first article boosts investor confidence, while the second raises concerns over legal issues."
        }},
        {{
          "Comparison": "Article 3 discusses Apple's stock performance positively, but Article 4 highlights supply chain disruptions.",
          "Impact": "Investors may feel uncertain due to conflicting perspectives."
        }}
      ]
    }}

    Remember just return the output result as json alone, do not provide any extra information.
    """

    response = llm.invoke(prompt)
    cleaned_data = response.content.strip('```json\n').strip('\n```')
    parsed_data = json.loads(cleaned_data)
    return parsed_data


def get_topic_overlap(articles):
    topic_count = defaultdict(int)

    # Count occurrences of each topic across all articles
    for article in articles:
        for topic in article['Topics']:
            topic_count[topic] += 1

    # Find common topics (appear in at least 2 articles)
    common_topics = [topic for topic, count in topic_count.items() if count > 1]

    # Find unique topics for each article
    unique_topics = []
    for article in articles:
        unique_topics.append([topic for topic in article['Topics'] if topic_count[topic] == 1])

    # Construct output
    return {
        "Topic Overlap": {
            "Common Topics": common_topics,
            **{f"Unique Topics in Article {i+1}": unique_topics[i] for i in range(len(articles))}
        }
    }


def final_sentiment(articles):
    summaries = []

    for art in articles:
        summaries.append(art['Summary'])

    final_prompt = f"""
            I will give you the summaries about the articles of the company I need you to generate the Final Sentiment
            Analysis for that company using those articles summaries.
            For Eg:
                "Tesla's latest news coverage is mostly positive. Potential stock growth expected."
            
            Here is the entire list of articles:
            {summaries}

            Remeber just give me the final sentiment analysis for that company and its reason with very short summary of above articles, do not give any extra information. 
        """

    final_analysis = llm.invoke(final_prompt)
    return final_analysis.content