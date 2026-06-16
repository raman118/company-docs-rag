import pytest
from src import retrieval

def test_stage4_retrieval():
    """Stage 4: Test Semantic Retrieval and Filtering"""
    queries = [
        ("how many days of annual leave do employees get", True),
        ("what is the password expiry policy", False), # Not in sample docs provided in stage 2 rewrite
        ("how do I get VPN access", True),
        ("what is the refund timeline", True),
        ("xyz123 gibberish query that should return no results", False)
    ]

    for query_text, should_have_results in queries:
        results = retrieval.retrieve(query_text)
        
        if should_have_results:
            assert len(results) > 0, f"Query '{query_text}' failed to return results."
            assert "content" in results[0]
            assert "source" in results[0]
            assert "score" in results[0]
            assert results[0]["score"] <= 0.7
        else:
            assert len(results) == 0, f"Query '{query_text}' unexpectedly returned results."
