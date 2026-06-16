import os
import sys
import glob
import logging
import argparse
import fitz  # PyMuPDF
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

def chunk_text(text, chunk_size=config.CHUNK_SIZE, overlap=config.CHUNK_OVERLAP):
    """Chunks text into word-based blocks with overlap."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        chunk = " ".join(words[start:start + chunk_size])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def get_collection(client, reset=False):
    """Retrieves or creates the ChromaDB collection, optionally resetting it."""
    if reset:
        try:
            client.delete_collection(name=config.CHROMA_COLLECTION)
            logger.info(f"Resetting collection: {config.CHROMA_COLLECTION}")
        except ValueError:
            pass  # Collection didn't exist
    
    return client.get_or_create_collection(
        name=config.CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )

def ingest_folder(folder_path, reset=False):
    """Main ingestion logic."""
    try:
        if not os.path.exists(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return

        logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
        model = SentenceTransformer(config.EMBEDDING_MODEL)

        logger.info(f"Connecting to ChromaDB at: {config.STORE_DIR}")
        client = chromadb.PersistentClient(path=str(config.STORE_DIR))
        collection = get_collection(client, reset=reset)

        files = []
        for ext in ('*.pdf', '*.txt', '*.md'):
            files.extend(glob.glob(os.path.join(folder_path, '**', ext), recursive=True))

        logger.info(f"Found {len(files)} potential files for ingestion.")

        processed_count = 0
        skipped_count = 0
        total_chunks = 0

        # Get existing sources if not resetting
        existing_sources = set()
        if not reset:
            results = collection.get(include=['metadatas'])
            if results and results['metadatas']:
                existing_sources = {m['source'] for m in results['metadatas']}

        for file_path in files:
            filename = os.path.basename(file_path)
            
            if not reset and filename in existing_sources:
                logger.warning(f"Skipping duplicate file: {filename}")
                skipped_count += 1
                continue

            logger.info(f"Processing: {filename}")
            file_chunks = []
            
            try:
                if filename.lower().endswith('.pdf'):
                    doc = fitz.open(file_path)
                    if doc.is_encrypted:
                        logger.warning(f"Skipping encrypted PDF: {filename}")
                        skipped_count += 1
                        doc.close()
                        continue
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        text = page.get_text()
                        if not text.strip():
                            continue
                        
                        chunks = chunk_text(text)
                        for i, chunk in enumerate(chunks):
                            file_chunks.append({
                                "id": f"{filename}_p{page_num+1}_c{i}",
                                "content": chunk,
                                "metadata": {"source": filename, "page": str(page_num+1), "chunk_index": i}
                            })
                    doc.close()
                else:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                        if not text.strip():
                            continue
                        
                        chunks = chunk_text(text)
                        for i, chunk in enumerate(chunks):
                            file_chunks.append({
                                "id": f"{filename}_c{i}",
                                "content": chunk,
                                "metadata": {"source": filename, "page": "N/A", "chunk_index": i}
                            })

                if file_chunks:
                    ids = [c['id'] for c in file_chunks]
                    documents = [c['content'] for c in file_chunks]
                    metadatas = [c['metadata'] for c in file_chunks]
                    embeddings = model.encode(documents).tolist()
                    
                    collection.add(
                        ids=ids,
                        embeddings=embeddings,
                        documents=documents,
                        metadatas=metadatas
                    )
                    total_chunks += len(file_chunks)
                    processed_count += 1
                else:
                    logger.warning(f"No valid text found in: {filename}")
                    skipped_count += 1

            except Exception as e:
                logger.error(f"Failed to process {filename}: {str(e)}")
                skipped_count += 1

        logger.info("--- Ingestion Summary ---")
        logger.info(f"Total files processed: {processed_count}")
        logger.info(f"Total chunks stored:    {total_chunks}")
        logger.info(f"Skipped files:          {skipped_count}")
        
        return {
            "processed": processed_count,
            "chunks": total_chunks,
            "skipped": skipped_count
        }

    except Exception as e:
        logger.error(f"Critical error during ingestion: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DocuQuery Ingestion CLI")
    parser.add_argument("--folder", type=str, required=True, help="Path to the folder containing documents")
    parser.add_argument("--reset", action="store_true", help="Wipe the collection before ingesting")
    
    args = parser.parse_args()
    ingest_folder(args.folder, reset=args.reset)
