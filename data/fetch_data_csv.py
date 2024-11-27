import requests
import csv
from dotenv import load_dotenv  # type: ignore
import os

load_dotenv()

# Set up the API key
api_key = os.environ.get("API_KEY")

if not api_key:
    print("Error: API key not found. Make sure it's set in the environment variables.")
    exit()

query = "inspiring success stories"
url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    articles = data["articles"]

    
    formatted_query = query.replace(" ", "_").lower()
    csv_file = f"news_data_{formatted_query}.csv"
    with open(csv_file, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        # Header
        writer.writerow(["Title", "Description", "Content", "URL", "Source", "PublishedAt"])

        # Article data
        for article in articles:
            writer.writerow([
                article["title"],
                article["description"],
                article["content"],
                article["url"],
                article["source"]["name"],
                article["publishedAt"]
            ])


    print(f"Data saved to '{csv_file}' successfully!")
else:
    print(f"Error: {response.status_code}")
