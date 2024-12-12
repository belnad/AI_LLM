# where we will implement ollama
from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Event,
    Context
)
from llama_index.core import Settings

import requests
import json
from datetime import date, timedelta

import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# from llama_index.utils.workflow import draw_all_possible_flows

class APIFetchEvent(Event):
    output: str
    
class StoreEvent(Event):
    output: str

class SummarizingEvent(Event):
    output: str
    
class ClassifyingEvent(Event):
    output: str
    
class NewsSummarizer(Workflow):
    @step
    async def fetch(self, ctx:Context, ev:StartEvent) -> APIFetchEvent | StopEvent:
        api_key = "cc0940ffb4804a62848cc2fcb78810c9"

        if not api_key:
            print("Error: API key not found. Make sure it's set in the environment variables.")
            return StopEvent()

        #TODO: will have to change
        query = "news of the day"
        # query = ev.query

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
            
            await ctx.set("articles", articles_data)
            return APIFetchEvent(query = ev.query)
    
    @step
    async def store(self,ctx:Context, ev:APIFetchEvent) -> StoreEvent|StopEvent:
        articles = await ctx.get("articles", default=None)
        if articles is None:
            print("Error loading articles")
            return StopEvent()
        print("Generating embeddings...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        article_embeddings = []
        
        for article in articles:
            # Utiliser le contenu ou la description pour générer les embeddings 
            content = article.get("content", "") or article.get("description", "")
            if content:
                embedding = model.encode(content)
                article_embeddings.append({
                    "embedding": embedding,
                    "metadata": {
                        "title": article["title"],
                        "url": article["url"],
                        "source": article["source"],
                        "publishedAt": article["publishedAt"]
                    }
                })
        print(f"Generated embeddings for {len(article_embeddings)} articles.")
        print("Storing embeddings in FAISS...")
        if not article_embeddings:
            print("No embeddings to store.")
            return None

        # Initialiser FAISS
        dimension = len(article_embeddings[0]["embedding"])
        index = faiss.IndexFlatL2(dimension)
        
        # Ajouter les embeddings à l'index
        embeddings_matrix = np.array([item["embedding"] for item in article_embeddings])
        index.add(embeddings_matrix)

        print(f"Stored {len(article_embeddings)} embeddings in the FAISS index.")

        await ctx.set("index", index)
        return StoreEvent()
    
    @step 
    async def summarize(self, ev:StoreEvent) -> SummarizingEvent:
        return SummarizingEvent()
    
    @step 
    async def classify(self, ev:SummarizingEvent) -> ClassifyingEvent:
        return ClassifyingEvent()
    
    @step 
    async def return_answer(self, ev:ClassifyingEvent | SummarizingEvent) -> StopEvent:
        return ClassifyingEvent()