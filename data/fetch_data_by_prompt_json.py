import requests
import json
from dotenv import load_dotenv  # type: ignore
import os

load_dotenv()

# Set up the API key
api_key = os.environ.get("API_KEY")


if not api_key:
    print("Error: API key not found. Make sure it's set in the environment variables.")
    exit()

# Ask the user for multiple search queries
user_queries = input("Enter your search queries, separated by commas (e.g., 'medicine, social media'): ")

# Split the input into individual queries
queries = [query.strip() for query in user_queries.split(",")]


all_articles = []

# Process each query
for query in queries:
    print(f"\nFetching articles for query: '{query}'...")
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        articles = data["articles"]

        # Add articles to the combined list, with query information
        for article in articles:
            all_articles.append({
                "query": query,
                "title": article["title"],
                "description": article["description"],
                "content": article["content"],
                "url": article["url"],
                "source": article["source"]["name"],
                "publishedAt": article["publishedAt"]
            })

        print(f"Fetched {len(articles)} articles for query '{query}'.")
    else:
        print(f"Error fetching data for query '{query}': {response.status_code}")


formatted_queries = "_".join([query.replace(" ", "").lower() for query in queries])
output_file = f"news_data_{formatted_queries}.json"


with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(all_articles, json_file, indent=4, ensure_ascii=False)

print(f"\nAll data saved to '{output_file}' successfully!")
