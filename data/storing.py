import json
from llama_index.core import Settings, VectorStoreIndex, download_loader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Étape 1 : Charger les articles depuis le fichier JSON
def load_articles(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as json_file:
            articles = json.load(json_file)
            print(f"Loaded {len(articles)} articles from '{file_name}'.")
            return articles
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        return []

# Étape 2 : Générer les embeddings des articles
def generate_embeddings(articles):
    print("Generating embeddings...")

    # Charger l'URL des 5 premiers articles (peut être modifier)
    urls = [article["url"] for article in articles[:5]]

    # Charger le modèle HuggingFace
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
    Settings.embed_model = embed_model  # Associer le modèle à la configuration globale

    # Charger les documents directement depuis les URL
    BeautifulSoupWebReader = download_loader("BeautifulSoupWebReader")
    loader = BeautifulSoupWebReader()
    documents = loader.load_data(urls=urls)

    # Générer un VectorStoreIndex avec les embeddings
    index = VectorStoreIndex.from_documents(documents)

    print("Embeddings have been generated and stored successfully!")    
    print(f"Generated embeddings for {len(documents)} articles.")
    return index

# Pipeline principal
def main():
    # Charger les articles
    articles = load_articles("articles.json")
    if not articles:
        return

    # Générer les embeddings
    article_embeddings = generate_embeddings(articles)
    if not article_embeddings:
        return

# Exécuter le script
if __name__ == "__main__":
    main()
