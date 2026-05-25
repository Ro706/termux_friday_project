import requests
from backend.TextToSpeech import speak
import datetime
import dotenv
import os

dotenv.load_dotenv()

class news:
    def __init__(self):
        self.url = f"https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey={os.getenv('NEWS_API')}"

    def news(self):
        try:
            news = requests.get(self.url).json()
            article = news.get("articles", [])
            news_article = []
            for arti in article:
                news_article.append(arti["title"])
            
            report = f"News Report for {datetime.datetime.now().strftime('%d-%m-%Y')}:\n"
            for i in range(min(10, len(news_article))):
                report += f"{i+1}. {news_article[i]}\n"
                speak(news_article[i])
            return report
        except Exception as e:
            return f"Error fetching news: {e}"

def news_report():
    obj = news()
    return obj.news()
    
if __name__ == "__main__":
    print(news_report())