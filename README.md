# **Project Description**

The **Daily News Summarizer and Analyst** aims to provide concise, categorized, and sentiment-analyzed news summaries based on user-provided themes or locations. The project will:

1. Fetch news articles dynamically via APIs or RSS feeds.
2. Store articles in a VectorStore for querying.
3. Use **Ollama** (local LLM) to:
    - Summarize articles.
    - Categorize them by themes or regions.
    - Perform sentiment analysis. (Positive, Neutral or negative News)
4. Present results to users in an interactive format (e.g., JSON, CLI, or web interface).

This project leverages **12GB of VRAM** provided by Google Cloud for running Ollama locally.

# Using
```
git clone https://github.com/belnad/AI_LLM.git
cd data
python3 luncher.py
```
