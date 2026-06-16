import chromadb
from sentence_transformers import SentenceTransformer

# Initialize model and db connection globally so they aren't reloaded on every function call
model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="./store/")
collection = client.get_or_create_collection(
    name="company_docs",
    metadata={"hnsw:space": "cosine"}
)

def retrieve(query: str, top_k: int = 5) -> list[dict]:
    query_embedding = model.encode(query).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=['documents', 'metadatas', 'distances']
    )
    
    output = []
    if not results['documents'] or not results['documents'][0]:
        return output
        
    docs = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]
    
    for doc, meta, dist in zip(docs, metadatas, distances):
        # Filter out chunks with cosine distance > 0.7 (weak matches)
        if dist > 0.7:
            continue
            
        output.append({
            "content": doc,
            "source": meta.get("source", "Unknown"),
            "page": meta.get("page", "N/A"),
            "score": dist
        })
        
    return output
