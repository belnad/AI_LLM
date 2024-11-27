import requests
import json
from dotenv import load_dotenv  # type: ignore
import os

load_dotenv()


api_key = os.environ.get("API_KEY")


if not api_key:
    print("Error: API key not found. Make sure it's set in the environment variables.")
    exit()

query = "positive impact and negative impact"

# Name of the file
formatted_query = query.replace(" ", "_").lower()  


url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    articles = data["articles"]

    # data
    articles_data = []
    for article in articles:
        articles_data.append({
            "title": article["title"],
            "description": article["description"],
            "content": article["content"],
            "url": article["url"],
            "source": article["source"]["name"],
            "publishedAt": article["publishedAt"]
        })

    
    json_file_name = f"news_data_{formatted_query}.json"
    with open(json_file_name, "w", encoding="utf-8") as json_file:
        json.dump(articles_data, json_file, indent=4, ensure_ascii=False)

    print(f"Data saved to '{json_file_name}' successfully!")
else:
    print(f"Error: {response.status_code}")
