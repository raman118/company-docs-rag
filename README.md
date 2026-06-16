# DocuQuery
> A production-grade RAG chatbot that answers questions grounded strictly in your company's internal documents — with zero hallucination and full source citations.

## Features
- **Strict Grounding**: Answers only from ingested documents, never from model training data.
- **Inline Citations**: Source filename and page number included on every factual claim.
- **Conflict Detection**: Flags contradictory information across multiple documents.
- **Local Embeddings**: No data leaves your machine during indexing (using `all-MiniLM-L6-v2`).
- **Multi-Format Support**: Processes PDF, TXT, and Markdown documents.
- **Clean UI**: Built with Streamlit for seamless document management and chat.

## Tech Stack
| Component | Technology |
|---|---|
| **LLM** | Google Gemini 1.5 Pro |
| **Vector DB** | ChromaDB (Local Persistence) |
| **Embeddings** | all-MiniLM-L6-v2 (Local) |
| **Frontend** | Streamlit |
| **PDF Parsing** | PyMuPDF (fitz) |

## Project Structure
```text
docuquery-root/
├── src/
│   ├── __init__.py
│   ├── ingest.py          # Document parsing and vector indexing
│   ├── retrieval.py       # Semantic search logic
│   ├── chat.py            # LLM orchestration and grounding
│   └── config.py          # Centralized configuration
├── tests/                 # Comprehensive test suite
├── data/
│   └── sample_docs/       # Reference documents
├── store/                 # ChromaDB persistent storage
├── uploaded_docs/         # Runtime uploads (gitignored)
├── app.py                 # Streamlit application entry point
├── requirements.txt       # Project dependencies
├── .env.example           # Environment template
├── .gitignore             # Git ignore rules
└── README.md              # Project documentation
```

## Setup

### 1. Clone and install
```bash
git clone https://github.com/raman118/company-docs-rag
cd company-docs-rag
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Open .env and add your GEMINI_API_KEY
```

### 3. Ingest sample documents
```bash
python -m src.ingest --folder data/sample_docs
```

### 4. Run the app
```bash
streamlit run app.py
```

## Testing (no API key required)
```bash
pytest tests/ -v
```

## How It Works
1.  **Ingestion**: Documents are parsed, split into 500-token chunks with overlap, and converted into embeddings locally.
2.  **Embedding**: Uses `sentence-transformers` to generate 384-dimensional vectors for every chunk.
3.  **Retrieval**: When you ask a question, the query is vectorized and compared against the database using cosine similarity.
4.  **Generation**: The most relevant chunks are injected into a strict system prompt and sent to Gemini 1.5 Pro to generate a cited, grounded response.
