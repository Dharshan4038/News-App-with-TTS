# News Sentiment Analysis and Text-to-Speech Application

This application fetches news articles for a specified company, analyzes their sentiment, extracts topics, generates a comprehensive analysis report, and converts the final sentiment summary to Hindi speech.

![image](https://github.com/user-attachments/assets/7e653b60-1839-4fd5-9558-05a13510110c)


## Table of Contents
- [Features](#features)
- [Project Setup](#project-setup)
- [Model Details](#model-details)
- [API Development](#api-development)
- [API Usage](#api-usage)
- [Assumptions & Limitations](#assumptions--limitations)

## Features

- **News Retrieval**: Fetches relevant news articles for any company using Google Custom Search API
- **Content Extraction**: Extracts and parses article content using the Newspaper3k library
- **Sentiment Analysis**: Analyzes the sentiment of news articles using LLaMa 3.3 (via Groq)
- **Topic Extraction**: Identifies key topics discussed in each article
- **Comparative Analysis**: Compares sentiment coverage across different articles
- **Topic Overlap Detection**: Identifies common and unique topics across articles
- **Hindi Translation**: Translates the final sentiment summary to Hindi
- **Text-to-Speech**: Converts the Hindi text to speech for audio playback
- **Interactive UI**: Clean Streamlit interface for user interaction

## Project Setup

### Prerequisites
- Python 3.8+
- API keys for:
  - Google Search API
  - Google Custom Search Engine ID (CX)
  - Groq API Key

### Installation

1. Clone the repository:
```bash
git clone https://huggingface.co/spaces/your-username/news-sentiment-analysis
cd news-sentiment-analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX=your_custom_search_engine_id
GROQ_API_KEY=your_groq_api_key
```

### Running Locally

Run the Streamlit application:
```bash
streamlit run app.py
```

In a separate terminal, start the FastAPI server:
```bash
uvicorn api:app --reload
```

### Deployment to Hugging Face Spaces

1. Create a new Space on Hugging Face with Streamlit SDK
2. Add your API keys as secrets in the Space settings
3. Push your code to the Space repository
4. The application will automatically build and deploy

## Model Details

### News Summarization
- **Model**: LLaMa 3.3 70B Versatile (via Groq API)
- **Purpose**: Generates concise summaries (150-160 words) of news articles
- **Prompt**: Structured to extract key points while maintaining readability

### Sentiment Analysis
- **Model**: LLaMa 3.3 70B Versatile
- **Purpose**: Classifies article sentiment as Positive, Negative, or Neutral
- **Implementation**: Single-label classification using LLM-based analysis

### Topic Extraction
- **Model**: LLaMa 3.3 70B Versatile
- **Purpose**: Identifies topics discussed in each article
- **Output**: List of topic strings representing key subjects in the article

### Comparative Sentiment Analysis
- **Model**: LLaMa 3.3 70B Versatile
- **Purpose**: Compares sentiment coverage across multiple articles
- **Processing**: Analyzes differences in how topics are covered across articles

### Text-to-Speech
- **Library**: gTTS (Google Text-to-Speech)
- **Language Support**: Hindi
- **Translation**: Uses Google Translator (via deep-translator library)

## API Development

The application uses FastAPI to create a RESTful API that interfaces with the news retrieval and analysis components.

### API Endpoints

#### GET `/`
- Returns a welcome message
- Usage: `curl http://localhost:8000/`

#### GET `/news/{company_name}`
- Fetches and summarizes news articles for a given company
- Parameters: `company_name` (string)
- Returns: List of article objects with summaries
- Usage: `curl http://localhost:8000/news/Tesla`

#### POST `/analyze/sentiment`
- Analyzes sentiment and extracts topics from articles
- Request Body: List of article objects and company name
- Returns: Comprehensive analysis including sentiment distribution, topic overlap, and final sentiment
- Usage (with Postman or curl):
  ```bash
  curl -X POST http://localhost:8000/analyze/sentiment \
    -H "Content-Type: application/json" \
    -d '{"articles":[...], "company_name":"Tesla"}'
  ```

### Testing with Postman

1. **GET Request to Fetch News**:
   - Create a new GET request in Postman
   - URL: `http://localhost:8000/news/Tesla` (replace Tesla with any company name)
   - Send the request to see the list of news articles with summaries

2. **POST Request for Sentiment Analysis**:
   - Create a new POST request in Postman
   - URL: `http://localhost:8000/analyze/sentiment`
   - Body (raw JSON): 
     ```json
     {
       "articles": [
         {
           "Title": "Example Article",
           "URL": "https://example.com",
           "Content": "Article content here",
           "Summary": "Summary of the article"
         }
       ],
       "company_name": "Example Company"
     }
     ```
   - Send the request to see the sentiment analysis results

## API Usage

The application integrates with multiple external APIs:

### Google Custom Search API
- **Purpose**: Fetch relevant news articles about a specified company
- **Integration**: Uses the `requests` library to make API calls
- **Parameters**:
  - `q`: Search query (company name + "Current News")
  - `num`: Number of results (default: 10)
  - Pagination support for fetching more results

### Groq API (LLaMa 3.3)
- **Purpose**: Natural language processing for summarization, sentiment analysis, and topic extraction
- **Integration**: Uses the `langchain_groq` library
- **Model**: "llama-3.3-70b-versatile"
- **Functions**:
  - Generate article summaries
  - Analyze sentiment
  - Extract topics
  - Compare sentiment across articles
  - Generate final sentiment analysis

### Google Translate API
- **Purpose**: Translate English text to Hindi
- **Integration**: Uses the `deep_translator` library
- **Usage**: Translates the final sentiment analysis for text-to-speech conversion

### Google Text-to-Speech (gTTS)
- **Purpose**: Convert Hindi text to speech
- **Integration**: Uses the `gtts` library
- **Output**: MP3 audio file of the Hindi text

## Assumptions & Limitations

- **News Source Diversity**: The application relies on Google Search results, which may not provide a balanced view of all news sources.
- **Language Support**: Currently only supports Hindi for text-to-speech conversion. Other languages would require additional implementation.
- **Article Processing**: Limited to processing the first ~6000 characters of each article due to model constraints.
- **API Rate Limits**: Subject to rate limitations of the Google Search API and Groq API.
- **Processing Time**: Generating summaries and analysis may take several seconds per article.
