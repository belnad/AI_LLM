import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


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
    return article_embeddings

# Étape 3 : Stocker les embeddings dans un VectorStore (FAISS)
def store_embeddings_in_faiss(embeddings):
    print("Storing embeddings in FAISS...")
    if not embeddings:
        print("No embeddings to store.")
        return None

    # Initialiser FAISS
    dimension = len(embeddings[0]["embedding"])
    index = faiss.IndexFlatL2(dimension)
    
    # Ajouter les embeddings à l'index
    embeddings_matrix = np.array([item["embedding"] for item in embeddings])
    index.add(embeddings_matrix)

    print(f"Stored {len(embeddings)} embeddings in the FAISS index.")
    return index

# Étape 4 : Tester les requêtes sur l'index FAISS
def test_query(index, embeddings, query_text):
    print(f"Testing query: '{query_text}'")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode(query_text)
    
    # Recherche dans FAISS
    k = 5  # Nombre de résultats à récupérer
    distances, indices = index.search(np.array([query_embedding]), k)
    
    # Afficher les résultats
    print("\nQuery Results:")
    for i, idx in enumerate(indices[0]):
        if idx < len(embeddings):
            result = embeddings[idx]
            print(f"{i+1}. Title: {result['metadata']['title']}")
            print(f"   Source: {result['metadata']['source']}")
            print(f"   URL: {result['metadata']['url']}")
            print(f"   Published At: {result['metadata']['publishedAt']}")
            print(f"   Distance: {distances[0][i]:.4f}\n")

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

    # Stocker les embeddings dans FAISS
    index = store_embeddings_in_faiss(article_embeddings)
    if not index:
        return

    # Tester une requête
    test_query(index, article_embeddings, "what news on global economy")

# Exécuter le script
if __name__ == "__main__":
    main()
