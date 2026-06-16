import subprocess
import chromadb
import os
import pytest

print("--- Stage 3: Test Ingestion ---")

def test_stage3():
    try:
        # Use the absolute path or relative path to the project file
        # Ensure we are in the root and calling docuquery/ingest.py
        # But wait, ingest.py uses ./chroma_store/ relative to where it's run.
        # Let's run it and then check.
        result = subprocess.run(["python", "-m", "src.ingest", "./data/sample_docs/"], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            pytest.fail(f"Ingestion process FAIL: {result.stderr}")
        
        client = chromadb.PersistentClient(path="./store/")
        collection = client.get_collection(name="company_docs")
        count = collection.count()
        print(f"Total chunks stored: {count}")
        
        assert count > 0
    except Exception as e:
        pytest.fail(f"Ingestion Test: FAIL ({e})")
