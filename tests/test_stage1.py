import pytest
import chromadb
from sentence_transformers import SentenceTransformer
import importlib.util
from src import config

def check_package(name):
    spec = importlib.util.find_spec(name)
    return spec is not None

def test_stage1_environment():
    """Stage 1: Environment and Dependency Check"""
    packages = ['google.generativeai', 'chromadb', 'streamlit', 'fitz', 'sentence_transformers', 'dotenv']
    missing = [p for p in packages if not check_package(p)]
    
    assert len(missing) == 0, f"Missing packages: {missing}"

    try:
        client = chromadb.PersistentClient(path=str(config.STORE_DIR))
        client.get_or_create_collection(name="test_connection")
    except Exception as e:
        pytest.fail(f"ChromaDB Initialization failed: {e}")

    try:
        SentenceTransformer(config.EMBEDDING_MODEL)
    except Exception as e:
        pytest.fail(f"SentenceTransformers model load failed: {e}")
