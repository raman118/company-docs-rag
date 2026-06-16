import sys
import os

# Retrieval test

from src.retrieval import retrieve

print("--- Stage 4: Test Retrieval ---")

def test_stage4():
    queries = [
        ("how many days of annual leave do employees get", True),
        ("what is the password expiry policy", True),
        ("how do I get VPN access", True),
        ("what is the refund timeline", True),
        ("xyz123 gibberish query that should return no results", False)
    ]

    overall_pass = True

    for query_text, expected_results in queries:
        print(f"\nQuery: {query_text}")
        results = retrieve(query_text)
        print(f"Number of chunks retrieved: {len(results)}")
        
        if len(results) > 0:
            top = results[0]
            print(f"Top chunk source: {top['source']}, score: {top['score']:.4f}")
            
        if expected_results:
            if len(results) == 0:
                overall_pass = False
        else:
            if len(results) > 0:
                overall_pass = False

    assert overall_pass
