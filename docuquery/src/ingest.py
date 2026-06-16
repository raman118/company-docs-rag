import os
import sys
import glob
import fitz  # PyMuPDF
import chromadb
from sentence_transformers import SentenceTransformer

def chunk_text(text, chunk_size=500, overlap=50):
    """
    Chunks text into sizes of roughly `chunk_size` words with `overlap` words.
    Using simple word splitting to approximate tokens.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        chunk = " ".join(words[start:start + chunk_size])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def main(folder_path):
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return

    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print("Initializing ChromaDB persistent client...")
    client = chromadb.PersistentClient(path="./store/")
    # Using cosine distance to filter out chunks with cosine distance > 0.7 later
    collection = client.get_or_create_collection(
        name="company_docs",
        metadata={"hnsw:space": "cosine"}
    )

    files = []
    for ext in ('*.pdf', '*.txt', '*.md'):
        files.extend(glob.glob(os.path.join(folder_path, '**', ext), recursive=True))

    print(f"Found {len(files)} files to ingest.")

    for file_path in files:
        filename = os.path.basename(file_path)
        print(f"Processing: {filename}")
        
        if filename.lower().endswith('.pdf'):
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if not text.strip():
                    continue
                
                chunks = chunk_text(text)
                for i, chunk in enumerate(chunks):
                    idx = f"{filename}_p{page_num+1}_c{i}"
                    embedding = model.encode(chunk).tolist()
                    collection.add(
                        ids=[idx],
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[{"source": filename, "page": str(page_num+1), "chunk_index": i}]
                    )
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
                if not text.strip():
                    continue
                
                chunks = chunk_text(text)
                for i, chunk in enumerate(chunks):
                    idx = f"{filename}_c{i}"
                    embedding = model.encode(chunk).tolist()
                    collection.add(
                        ids=[idx],
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[{"source": filename, "page": "N/A", "chunk_index": i}]
                    )

    print("Ingestion complete.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <folder_path>")
        sys.exit(1)
    main(sys.argv[1])
