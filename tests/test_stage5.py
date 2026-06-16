import os
import pytest

def test_stage5_imports():
    """Stage 5: Module Health and Import Checks"""
    # Mock API Key for import safety
    os.environ["GEMINI_API_KEY"] = "mock_key"
    
    try:
        from src import chat
        assert hasattr(chat, 'ask')
        assert hasattr(chat, 'SYSTEM_PROMPT')
    except Exception as e:
        pytest.fail(f"Chat module import failed: {e}")
