# **Project Description**

The **Daily News Summarizer and Analyst** aims to provide concise, categorized, and sentiment-analyzed news summaries based on user-provided themes or locations. The project will:

1. Fetch news articles dynamically via APIs or RSS feeds.
2. Store articles in a VectorStore for querying.
3. Use **Ollama** (local LLM) to:
    - Summarize articles.
    - Categorize them by themes or regions.
    - Perform sentiment analysis. (Positive, Neutral or negative News)
4. Present results to users in an interactive format (web interface).

This project leverages **12GB of VRAM** provided by Google Cloud for running Ollama locally.

This project uses Streamlit as a framework for the user's web interface.

# Install
1. Install ollama and llama3.2
```
curl -fsSL https://ollama.com/install.sh | sh
ollama serve&
```
```
ollama run llama3.2 
```
2. Clone this repository.
```
git clone https://github.com/belnad/AI_LLM.git && cd AI_LLM
```

### How to use the web interface

1. Install: pip install streamlit
2. Run: streamlit run users_CLI.py
3. If the command above doesn't work, use this command instead: python -m streamlit run users_CLI.py 
4. You can switch between the home page and the results page with the navigation bar at the left of the website
![App Screenshot](./img_/navBar_home.png)

5. You doesn't need to fill all the section of the home page to have a result (one is enough, but to improve the results you can fill all the section)

6. To see the results of your search once you've clicked on the process button, click on the results button in the navigation bar.
![App Screenshot](./img_/Process.png)
![App Screenshot](./img_/navBar_results.png)

# setup
```
git clone https://github.com/belnad/AI_LLM.git
cd AI_LLM
python3 setup.py
```
