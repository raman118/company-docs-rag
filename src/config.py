import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
STORE_DIR = ROOT_DIR / "store"
UPLOAD_DIR = ROOT_DIR / "uploaded_docs"
SAMPLE_DOCS_DIR = ROOT_DIR / "data" / "sample_docs"

# Test isolation
if "PYTEST_CURRENT_TEST" in os.environ:
    STORE_DIR = ROOT_DIR / "test_store"


# ChromaDB
CHROMA_COLLECTION = "company_docs"

# Embedding
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Chunking
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Retrieval
TOP_K = 5
DISTANCE_THRESHOLD = 0.7

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-pro"
MAX_OUTPUT_TOKENS = 2048
