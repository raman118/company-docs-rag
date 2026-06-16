import pytest
import sys
import os
import chromadb
import fitz
from sentence_transformers import SentenceTransformer
import importlib.util

def check_package(name):
    spec = importlib.util.find_spec(name)
    return spec is not None

print("--- Stage 1: Environment Check ---")

def test_stage1():
    packages = ['google.generativeai', 'chromadb', 'streamlit', 'fitz', 'sentence_transformers', 'dotenv']
    missing = []
    for p in packages:
        if check_package(p):
            print(f"Package {p}: INSTALLED")
        else:
            print(f"Package {p}: MISSING")
            missing.append(p)

    assert len(missing) == 0

    try:
        # Check if we can initialize ChromaDB in the store path
        client = chromadb.PersistentClient(path="./store/")
        collection = client.get_or_create_collection(name="test_collection")
        print("ChromaDB Initialization: PASS")
    except Exception as e:
        pytest.fail(f"ChromaDB Initialization: FAIL ({e})")

    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("SentenceTransformers Load: PASS")
    except Exception as e:
        pytest.fail(f"SentenceTransformers Load: FAIL ({e})")

    try:
        import fitz
        print("PyMuPDF Import: PASS")
    except Exception as e:
        pytest.fail(f"PyMuPDF Import: FAIL ({e})")
