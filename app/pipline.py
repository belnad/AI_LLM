from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Event,
    Context
)
from llama_index.core import Settings, VectorStoreIndex, Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.web import BeautifulSoupWebReader
from llama_index.llms.ollama import Ollama

import json
import urllib.request

from dotenv import load_dotenv
import os

class APIFetchEvent(Event):
    query: str

class StoreEvent(Event):
    query: str

class SummarizingEvent(Event):
    query: str

class ClassifyingEvent(Event):
    query: str

class NewsSummarizer(Workflow):
    Settings.embedding_model = HuggingFaceEmbedding()
    Settings.llm = Ollama(model="llama3.2")

    @step
    async def fetch(self, ctx: Context, ev: StartEvent) -> APIFetchEvent :
        """
        Fetches news articles using the GNews API based on the query and country parameters.
        Saves the articles' metadata to a JSON file and stores the data in the workflow context.

        Args:
            ctx (Context): Workflow context for storing and retrieving data.
            ev (StartEvent): Event containing query parameters (query, country).

        Returns:
            APIFetchEvent: Custom event signaling the completion of the fetch operation.
        """

        # Extract query parameters from the StartEvent
        global url
        query = ev.query  # Search keyword for news articles

        # Extract filter parameters from StartEvent
        filters = ev.filters

        # Load API key from the .env file
        load_dotenv()
        apikey = os.environ.get('API_KEY')  # Retrieve the API key for GNews

        # Initialize an empty list to store article data
        articles_data = []

        # Construct the GNews API request URL
        if  "category" not in filters and "country" in filters:
            url = f"https://newsapi.org/v2/top-headlines?q={query}&lang=en&country={filters['country']}&max=5&apikey={apikey}"
        elif "category" not in filters and "country" not in filters:
            url = f"https://newsapi.org/v2/top-headlines?q={query}&lang=en&max=5&apikey={apikey}"
        elif "category" in filters and "country" in filters:
            url = f"https://newsapi.org/v2/top-headlines?q={query}&category={filters['category']}&lang=en&country={filters['country']}&max=5&apikey={apikey}"
        elif "category" in filters and "country" not in  filters:
            url = f"https://newsapi.org/v2/top-headlines?q={query}&category={filters['category']}&lang=en&max=5&apikey={apikey}"

        # Send a request to the GNews API
        with urllib.request.urlopen(url) as response:
            # Parse the API response as JSON
            data = json.loads(response.read().decode("utf-8"))

            # Extract the articles section from the response
            articles = data.get("articles", [])  # Safely get 'articles' to avoid KeyError

            # Loop through each article and extract relevant fields
            for article in articles:
                if article["title"] != "[Removed]":
                    articles_data.append({
                        "title": article["title"],                # Article title
                        "description": article["description"],    # Article description
                        "url": article["url"],                    # URL to the article
                        "source": article["source"]["name"],      # News source name
                        "publishedAt": article["publishedAt"]     # Publication date
                    })

        # Save the fetched articles to a local JSON file for later steps
        json_file_name = "articles.json"
        with open(json_file_name, "w", encoding="utf-8") as json_file:
            json.dump(articles_data, json_file, indent=4, ensure_ascii=False)

        print(f"Data saved to '{json_file_name}' successfully!")

        # Store the fetched articles data in the workflow context for the next steps
        await ctx.set("articles", articles_data)

        # Return a custom APIFetchEvent to signal that fetching was successful
        return APIFetchEvent(query=query)

    @step
    async def store(self, ctx: Context, ev: APIFetchEvent) -> StoreEvent | StopEvent:
        """
        Loads article metadata from a JSON file, fetches full content for each article,
        creates Document objects, generates embeddings, and stores the results in the workflow context.

        Args:
            ctx (Context): Workflow context for storing and retrieving data.
            ev (APIFetchEvent): Event containing the query information.

        Returns:
            StoreEvent: Custom event signaling successful document storage and embedding.
            StopEvent: Stops the workflow in case of failure (e.g., file not found).
        """
        try:
            # Load the articles JSON file containing metadata fetched in the previous step
            with open("articles.json", "r", encoding="utf-8") as json_file:
                articles = json.load(json_file)
                print("Loaded Articles:", articles[:2])  # Print the first 2 articles for verification
        except FileNotFoundError:
            # If the file does not exist, stop the workflow
            print("Error: File not found.")
            return StopEvent()

        print("Fetching article content using BeautifulSoupWebReader...")

        # Initialize the web content reader
        loader = BeautifulSoupWebReader()

        # List to store Document objects
        documents = []

        # Iterate through the articles and fetch their full content
        for i, item in enumerate(articles[:2]):
            url = item.get("url", "")  # Extract the URL of the article
            print(f"Processing URL {i + 1}/{len(articles)}: {url}")

            # Default content in case fetching fails
            content = "Content not available"
            # Attempt to load the content using BeautifulSoupWebReader
            content = loader.load_data([url])
            if content:
                content = content[0].text  # Extract the text from the loaded content
            else:
                print(f"Error fetching content from URL: {url}")

            # Create a Document object combining content and metadata
            document = Document(
                text=content,
                metadata={
                    "title": item.get("title", "unknown"),  # Title of the article
                    "description": item.get("description", "general"),  # Description of the article
                    "url": url,  # URL of the article
                    "date": item.get("publishedAt", "unknown"),  # Publication date
                    "source": item.get("source", "unknown"),  # Source name
                },
                metadata_seperator="::",  # Define how metadata pairs are separated
                metadata_template="{key}=>{value}",  # Template for metadata formatting
                text_template="Metadata: {metadata_str}\n-----\nContent: {content}",  # Template for Document text
            )
            documents.append(document)  # Add the Document to the list

        # Save the processed Document objects to the workflow context
        await ctx.set("documents", documents)

        # Generate embeddings for the documents using the configured embedding model
        index = VectorStoreIndex.from_documents(
            documents,
            embed_model=Settings.embedding_model,
            show_progress=True  # Display progress while generating embeddings
        )

        print("\nEmbeddings have been generated and stored successfully!")
        print(f"Generated embeddings for {len(documents)} articles.\n")

        # Save the generated index to the workflow context
        await ctx.set("index", index)

        # Return a custom StoreEvent to signal successful completion
        return StoreEvent(query=ev.query)

    @step
    async def summarize_and_classify(self, ctx: Context, ev: StoreEvent) -> SummarizingEvent:
        """
        Summarizes and classifies the sentiment of articles stored in the context.
        Uses the query engine built from the document embeddings to process each article.

        Args:
            ctx (Context): Workflow context to retrieve and store data.
            ev (StoreEvent): Event signaling that documents are ready for processing.

        Returns:
            SummarizingEvent: Event signaling successful summarization and classification.
        """
        print("----------------------------\n\t\t\tSummarizing and Classifying Articles...\n-----------------------------------")

        # Retrieve the document index and documents from the workflow context
        index = await ctx.get("index")  # Index containing embeddings and query engine
        documents = await ctx.get("documents")  # List of processed Document objects

        # Create a query engine from the document index for natural language querying
        query_engine = index.as_query_engine()

        # List to store the summarization and sentiment classification results
        results = []

        # Iterate through each document to summarize and classify sentiment
        for i, article in enumerate(documents):
            print(f"Processing article {i + 1}/{len(documents)}: {article.metadata['title']}")

            # Step 1: Generate a summary for the article
            summarize_query = f"Summarize this article: {article.metadata['title']}"
            summary_response = query_engine.query(summarize_query)  # Query the engine for summarization
            summary = summary_response.response.strip()  # Extract and clean the response

            # Step 2: Classify the sentiment of the summary
            classify_prompt = f"""Analyze the following article summary and classify the sentiment
            as 'Positive', 'Neutral', or 'Negative'. Provide only the sentiment label.

            Summary: {summary}"""
            sentiment_response = query_engine.query(classify_prompt)  # Query for sentiment classification
            sentiment = sentiment_response.response.strip()  # Extract and clean the sentiment label

            # Append the summary and sentiment classification results to the results list
            results.append({
                "title": article.metadata["title"],  # Article title
                "url": article.metadata["url"],      # Article URL
                "source": article.metadata["source"], # Source
                "summary": summary,                  # Generated summary
                "sentiment": sentiment               # Classified sentiment
            })

        # Store the final results in the workflow context for downstream use
        await ctx.set("results", results)

        # Return an event indicating successful summarization and classification
        return SummarizingEvent(query="Summarized and Classified Articles")

    @step
    async def return_answer(self, ctx: Context, ev: SummarizingEvent) -> StopEvent:
        """
        Final step: Retrieves the summarized and classified results from the workflow context,
        prints them for verification, and returns the results as structured data.

        Args:
            ctx (Context): Workflow context to retrieve the summarized results.
            ev (SummarizingEvent): Event indicating summarization and classification are complete.

        Returns:
            StopEvent: Final event that stops the workflow and outputs the results as structured data.
        """
        # Retrieve the results (list of summaries and sentiments) from the context
        results = await ctx.get("results")

        # Print the final results to the console for verification
        print("Final Results: Summaries and Sentiments")
        for result in results:
            print(f"Title: {result['title']}")  # Print the article title
            print(f"Summary: {result['summary']}")  # Print the article summary
            print(f"Sentiment: {result['sentiment']}")  # Print the sentiment classification
            print("-" * 50)  # Separator for better readability

        # Return a StopEvent containing the results as structured data
        return StopEvent(result={"articles": results})


# Function to execute the NewsSummarizer workflow
async def run_news_workflow(query: str, filters: dict):
    # Instantiate the workflow
    news_summarizer = NewsSummarizer(timeout=None, verbose=True)

    # Run the workflow with inputs
    result = await news_summarizer.run(query=query, filters=filters)
    articles = result["articles"]
    return articles # return result to frontend

# print("------------------\n", "Debug : ", result, "\n-------------------")