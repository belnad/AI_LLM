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
To run the code you have to have Ollama running on your machine and llama3.2 .
### running on colab

```
!pip install colab-xterm
````
load xterm
```
%load_ext colabxterm
````
run xterm
```
xterm
````

run commands in command line:
```
curl -fsSL https://ollama.com/install.sh | sh
ollama serve & 
ollama pull llama3.2

```
