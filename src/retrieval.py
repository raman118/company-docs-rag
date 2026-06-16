import logging
import chromadb
from sentence_transformers import SentenceTransformer
from src import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s — %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Singleton-like initialization
_model = None
_client = None
_collection = None

def get_resources():
    """Initializes and returns shared resources."""
    global _model, _client, _collection
    if _model is None:
        logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        _model = SentenceTransformer(config.EMBEDDING_MODEL)
    if _client is None:
        logger.info(f"Connecting to ChromaDB at: {config.STORE_DIR}")
        _client = chromadb.PersistentClient(path=str(config.STORE_DIR))
        _collection = _client.get_or_create_collection(
            name=config.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"}
        )
    return _model, _collection

def retrieve(query: str, top_k: int = config.TOP_K) -> list[dict]:
    """Retrieves the top_k most relevant document chunks for a query."""
    model, collection = get_resources()
    
    logger.info(f"Retrieving top {top_k} chunks for query: '{query}'")
    query_embedding = model.encode(query).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=['documents', 'metadatas', 'distances']
    )
    
    output = []
    if not results['documents'] or not results['documents'][0]:
        logger.warning("No chunks returned from ChromaDB.")
        return output
        
    docs = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]
    
    for doc, meta, dist in zip(docs, metadatas, distances):
        # Filter out chunks with distance > threshold (weaker matches)
        if dist > config.DISTANCE_THRESHOLD:
            continue
            
        output.append({
            "content": doc,
            "source": meta.get("source", "Unknown"),
            "page": meta.get("page", "N/A"),
            "score": dist
        })
        
    if not output:
        logger.warning(f"All {len(docs)} retrieved chunks were above distance threshold ({config.DISTANCE_THRESHOLD}).")
        
    return output

def get_collection_count() -> int:
    """Returns the total number of chunks in the collection."""
    try:
        _, collection = get_resources()
        return collection.count()
    except Exception as e:
        logger.error(f"Failed to get collection count: {e}")
        return 0

def format_chunks_for_prompt(chunks: list[dict]) -> str:
    """Formats retrieved chunks into the XML block for the LLM prompt."""
    if not chunks:
        return ""
        
    xml_blocks = ["<retrieved_chunks>"]
    for i, chunk in enumerate(chunks):
        block = (
            f"[CHUNK {i+1}]\n"
            f"Source: {chunk['source']}\n"
            f"Page: {chunk['page']}\n"
            f"Score: {chunk['score']:.4f}\n"
            f"Content: {chunk['content']}\n"
        )
        xml_blocks.append(block)
    xml_blocks.append("</retrieved_chunks>")
    
    return "\n".join(xml_blocks)
