import requests
import json
from datetime import date, timedelta

# my api key
api_key = "cc0940ffb4804a62848cc2fcb78810c9"

if not api_key:
    print("Error: API key not found. Make sure it's set in the environment variables.")
    exit()

query = "news of the day"

url = "https://newsapi.org/v2/everything" 
params = { # request parameters
    "q": query,
    "apiKey": api_key,
    "from": (date.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
    "sortBy": "popularity",
    "pageSize": 1,  # Maximum articles per page
    "page": 1
}

articles_data = []

# Loop to retrieve all available article pages.
while True:
    response = requests.get(url, params=params)
    # Provides detailed information if an HTTP error occurs
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        break
    
    data = response.json()
    # Checks if the articles field exists in the JSON response before using it
    if "articles" not in data:
        print("Error: Unexpected response format.")
        break

    articles = data["articles"]
    if not articles:
        break  # Stop if no more articles are returned
    
    for article in articles:
        articles_data.append({
            "title": article["title"],
            "description": article["description"],
            "content": article["content"],
            "url": article["url"],
            "source": article["source"]["name"],
            "publishedAt": article["publishedAt"]
        })

    params["page"] += 1  # Move to the next page

# create json file for next process
json_file_name = "articles.json"
with open(json_file_name, "w", encoding="utf-8") as json_file:
    json.dump(articles_data, json_file, indent=4, ensure_ascii=False)

print(f"Data saved to '{json_file_name}' successfully!")
