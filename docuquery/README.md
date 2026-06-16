# DocuQuery
A RAG chatbot over company documents using ChromaDB and Claude.

## Setup
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

## Ingest Documents
python -m src.ingest --folder data/sample_docs

## Run App
streamlit run app.py

## Run Tests (no API key required)
pytest tests/
