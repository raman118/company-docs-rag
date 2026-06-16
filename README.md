# DocuQuery
RAG-powered chatbot for grounded question answering over internal company documents.

![Python Version](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-orange)

DocuQuery provides a secure, locally-indexed retrieval-augmented generation pipeline that transforms internal documents into a searchable knowledge base. By utilizing local embeddings and a strictly grounded prompt architecture, the system ensures that responses are derived exclusively from the provided context with mandatory source citations. This approach eliminates external embedding dependencies and minimizes the risk of large language model hallucinations.

## Architecture

User Query → Embedding (all-MiniLM-L6-v2) → ChromaDB Retrieval → Context Assembly → Claude (claude-opus-4-8) → Cited Response

- **Embedding**: Query vectorization using local sentence-transformers to avoid external API calls for indexing.
- **Retrieval**: Cosine similarity search against local ChromaDB with a distance threshold filter of 0.7.
- **Augmentation**: Context construction using 500-token chunks with 50-token overlap for optimal semantic density.
- **Generation**: Strict grounding via Claude claude-opus-4-8 to produce concise, cited answers.

## Features

- Local vector storage using ChromaDB with persistence to the filesystem.
- Multi-format support for PDF (via PyMuPDF), TXT, and MD files.
- Automated chunking with sliding window overlap to maintain context across boundaries.
- Citation-first response logic requiring inline source and page references.
- Streamlit-based interface for real-time chat and document management.

## Project Structure

```text
docuquery/
├── src/
│   ├── ingest.py       # Document parsing and vector database indexing
│   ├── retrieval.py    # Semantic search and similarity filtering
│   └── chat.py         # LLM orchestration and grounding logic
├── tests/              # Unit and integration test suite
├── data/
│   └── sample_docs/    # Reference documents for initial setup and testing
├── store/              # Local ChromaDB persistent storage directory
├── app.py              # Streamlit web application entry point
├── requirements.txt    # Project dependencies
└── .env.example        # Environment variable template
```

## Quickstart

- Python 3.9+
- Anthropic API Key

```bash
git clone https://github.com/your-repo/docuquery.git
cd docuquery
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
python -m src.ingest --folder data/sample_docs
streamlit run app.py
```

## Usage

### Ingesting Documents
Run the ingestion script on a directory containing your PDF, TXT, or MD files:
```bash
python -m src.ingest --folder /path/to/your/documents
```

### Starting the Chatbot
Launch the UI to interact with the indexed documents:
```bash
streamlit run app.py
```

### Example Interaction
**User**: What is the company policy on remote work?

**Assistant**: Employees are allowed to work remotely up to two days per week with prior manager approval. [Source: hr_policy.txt, Page: 2]

## Configuration

| Variable | Description | Required |
| :--- | :--- | :--- |
| ANTHROPIC_API_KEY | API key for Claude claude-opus-4-8 access | Yes |

## Running Tests

Execute the test suite using pytest. All tests are designed to run without a valid API key by mocking the generation layer.
```bash
pytest tests/
```

## Contributing

1. Fork the repository.
2. Create a feature branch from main.
3. Ensure all tests pass.
4. Submit a pull request with a detailed description of changes.

## License

This project is licensed under the MIT License.
