import sys
import os
import pytest

print("--- Stage 5: Module Import Test ---")

def test_stage5():
    # Mock GEMINI_API_KEY to prevent chat.py from failing if it checks on import
    os.environ["GEMINI_API_KEY"] = "mock_key"

    try:
        from src import chat
        print("chat.py import: PASS")
    except Exception as e:
        pytest.fail(f"chat.py import: FAIL ({e})")
