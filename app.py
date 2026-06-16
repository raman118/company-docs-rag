import streamlit as st
import os
import logging
from src import config, ingest, retrieval, chat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page Config
st.set_page_config(
    page_title="DocuQuery",
    layout="wide",
    page_icon="🔍"
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.markdown("# 🔍 DocuQuery")
    st.divider()
    
    # Document Upload Section
    st.header("Upload Documents")
    uploaded_files = st.file_uploader(
        "Supported formats: PDF, TXT, MD",
        accept_multiple_files=True,
        type=['pdf', 'txt', 'md']
    )
    
    if st.button("Ingest Documents", use_container_width=True):
        if uploaded_files:
            with st.status("Processing documents...", expanded=True) as status:
                st.write("Saving uploaded files...")
                os.makedirs(config.UPLOAD_DIR, exist_ok=True)
                
                # Clean old uploads to prevent re-ingesting stale files
                for f in os.listdir(config.UPLOAD_DIR):
                    os.remove(os.path.join(config.UPLOAD_DIR, f))
                
                for file in uploaded_files:
                    file_path = config.UPLOAD_DIR / file.name
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                
                st.write("Ingesting into vector database...")
                try:
                    summary = ingest.ingest_folder(str(config.UPLOAD_DIR))
                    st.session_state.messages = [] # Clear chat history on new data
                    status.update(label="Ingestion complete!", state="complete", expanded=False)
                    st.success(
                        f"**Ingestion Summary:**\n"
                        f"- Files Processed: {summary['processed']}\n"
                        f"- Chunks Stored: {summary['chunks']}\n"
                        f"- Files Skipped: {summary['skipped']}"
                    )
                except Exception as e:
                    status.update(label="Ingestion failed!", state="error")
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please upload files first.")

    st.divider()
    
    # Stats Section
    st.header("Collection Stats")
    try:
        count = retrieval.get_collection_count()
        st.metric("Total Chunks", count)
    except Exception:
        st.metric("Total Chunks", 0)
    
    st.divider()
    
    # Settings Section
    st.header("Settings")
    top_k = st.slider("Top-K (Retrieval Depth)", min_value=1, max_value=10, value=config.TOP_K)

# Main Area
st.title("DocuQuery — Company Knowledge Assistant")
st.subheader("Ask questions grounded in your company documents")

# Check if collection is empty
try:
    if retrieval.get_collection_count() == 0:
        st.info("No documents ingested yet. Upload documents from the sidebar to get started.")
except Exception:
    st.info("No documents ingested yet. Upload documents from the sidebar to get started.")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("View Retrieved Sources"):
                for i, source in enumerate(message["sources"]):
                    st.markdown(f"**Source {i+1}: {source['source']} (Page: {source['page']})**")
                    st.caption(f"Relevance Score: {source['score']:.4f}")
                    st.text(source['content'])
                    st.divider()

# Chat Input
if prompt := st.chat_input("Ask a question about your documents..."):
    # User message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating answer..."):
            # We call retrieval directly here to pass sources to session state
            sources = retrieval.retrieve(prompt, top_k=top_k)
            
            if not sources:
                response_text = "I don't have enough information in the provided documents to answer this. Please consult the relevant team or check the source document directly."
            else:
                # Call chat logic
                response_text = chat.ask(prompt, top_k=top_k)
            
            st.markdown(response_text)
            
            # Show sources expander
            if sources:
                with st.expander("View Retrieved Sources"):
                    for i, source in enumerate(sources):
                        st.markdown(f"**Source {i+1}: {source['source']} (Page: {source['page']})**")
                        st.caption(f"Relevance Score: {source['score']:.4f}")
                        st.text(source['content'])
                        st.divider()
            
            # Save to history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response_text,
                "sources": sources
            })
