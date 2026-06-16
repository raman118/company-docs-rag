import chromadb
import pytest
from src import config, ingest

def test_stage3_ingestion():
    """Stage 3: Test Document Ingestion Pipeline"""
    try:
        # Run ingestion with reset to ensure clean state
        summary = ingest.ingest_folder(str(config.SAMPLE_DOCS_DIR), reset=True)
        
        assert summary["processed"] > 0
        assert summary["chunks"] > 0
        
        # Verify in ChromaDB
        client = chromadb.PersistentClient(path=str(config.STORE_DIR))
        collection = client.get_collection(name=config.CHROMA_COLLECTION)
        assert collection.count() == summary["chunks"]
        
    except Exception as e:
        pytest.fail(f"Ingestion Test failed: {e}")
