import streamlit as st
from utils import fetch_news_articles, analyze_sentiment
import api
from gtts import gTTS
import json
import base64
from deep_translator import GoogleTranslator
import os

# Function to translate english to hindi
def translate_to_hindi(text):
    translator = GoogleTranslator(source='en', target='hi')
    translation = translator.translate(text)
    return translation

# Function to convert Hindi text to audio format
def text_to_speech(text, lang='hi'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("output.mp3")
    return "output.mp3"


def main():
    st.title("News Summarization and Text-to-Speech Application")
    
    # Input for company name
    company_name = st.text_input("Enter Company Name:")
    
    if st.button("Generate Report"):
        with st.spinner("Fetching news articles..."):
            # Call the API to get news articles
            try:
                articles = api.get_news_articles(company_name)
                
                if not articles or len(articles) == 0:
                    st.error(f"No articles found for {company_name}. Please try another company name.")
                    return
                
                # Display number of articles found
                st.success(f"Found {len(articles)} articles for {company_name}")

                # Generate a report and convert it to audio format
                final_report = api.analyze_articles_sentiment(articles,company_name)
                hindi_text = translate_to_hindi(final_report["Comparative Sentiment Score"]["Final Sentiment"])
                audio_file = text_to_speech(hindi_text)
                

                st.write(final_report)

                st.subheader("Audio of News Summary")
                st.audio(audio_file, format='audio/mp3')
                
                
               
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()