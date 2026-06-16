import streamlit as st
import os
import logging
from src import config, ingest, retrieval, chat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_resource
def load_rag_resources():
    """Caches the heavy embedding model and DB connection."""
    return retrieval.get_resources()

# Page Config
st.set_page_config(
    page_title="DocuQuery",
    layout="wide",
    page_icon="🔍"
)

# Global CSS
st.markdown("""
<style>
/* Reset & Base */
* { box-sizing: border-box; }

[data-testid="stAppViewContainer"] {
    background-color: #0A0A0A;
}

[data-testid="stSidebar"] {
    background-color: #111111;
    border-right: 1px solid #1E1E1E;
    padding-top: 2rem;
}

[data-testid="stSidebar"] * {
    font-family: 'Inter', 'SF Pro Display', sans-serif;
}

/* Hide Streamlit branding */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* Sidebar logo */
.dq-logo {
    font-size: 1.1rem;
    font-weight: 600;
    color: #E8E8E8;
    letter-spacing: 0.02em;
    padding: 0 1rem 2rem 1rem;
    border-bottom: 1px solid #1E1E1E;
    margin-bottom: 1.5rem;
}

.dq-logo span {
    color: #6C63FF;
}

/* Sidebar section labels */
.dq-section-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #444444;
    padding: 0 1rem;
    margin-bottom: 0.75rem;
}

/* Stat display */
.dq-stat {
    font-size: 2rem;
    font-weight: 300;
    color: #E8E8E8;
    line-height: 1;
    padding: 0 1rem;
}

.dq-stat-label {
    font-size: 0.75rem;
    color: #444444;
    padding: 0.25rem 1rem 0 1rem;
}

/* Main area */
.dq-main-header {
    font-size: 1.75rem;
    font-weight: 600;
    color: #E8E8E8;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}

.dq-main-sub {
    font-size: 0.875rem;
    color: #444444;
    margin-bottom: 3rem;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    padding: 1rem 0 !important;
    border-bottom: 1px solid #1A1A1A !important;
}

[data-testid="stChatMessage"]:last-child {
    border-bottom: none !important;
}

/* User message */
[data-testid="stChatMessage"][data-testid*="user"] {
    background-color: #111111 !important;
    border-radius: 4px !important;
    padding: 1rem !important;
}

/* Input */
[data-testid="stChatInput"] {
    border-top: 1px solid #1E1E1E !important;
    background-color: #0A0A0A !important;
}

[data-testid="stChatInput"] textarea {
    background-color: #111111 !important;
    border: 1px solid #1E1E1E !important;
    border-radius: 4px !important;
    color: #E8E8E8 !important;
    font-size: 0.875rem !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: #6C63FF !important;
    box-shadow: none !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background-color: transparent !important;
    border: 1px dashed #2A2A2A !important;
    border-radius: 4px !important;
    padding: 0.5rem !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: #6C63FF !important;
}

/* Buttons */
.stButton > button {
    background-color: #6C63FF !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 4px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    padding: 0.5rem 1rem !important;
    width: 100% !important;
    transition: opacity 0.15s ease !important;
}

.stButton > button:hover {
    opacity: 0.85 !important;
    background-color: #6C63FF !important;
}

/* Slider */
[data-testid="stSlider"] > div > div > div > div {
    background-color: #6C63FF !important;
}

/* Expander (sources) */
[data-testid="stExpander"] {
    background-color: #111111 !important;
    border: 1px solid #1E1E1E !important;
    border-radius: 4px !important;
    margin-top: 0.5rem !important;
}

[data-testid="stExpander"] summary {
    font-size: 0.75rem !important;
    color: #444444 !important;
    letter-spacing: 0.04em !important;
}

/* Dividers */
hr {
    border-color: #1E1E1E !important;
    margin: 1.5rem 0 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0A0A0A; }
::-webkit-scrollbar-thumb { background: #2A2A2A; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #6C63FF; }
</style>
""", unsafe_allow_html=True)

# Ensure resources are loaded
with st.spinner("Initializing AI engine..."):
    load_rag_resources()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    # Logo
    st.markdown('<div class="dq-logo">Docu<span>Query</span></div>', unsafe_allow_html=True)

    # Upload section
    st.markdown('<div class="dq-section-label">Documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    ingest_btn = st.button("Ingest Documents")

    if ingest_btn:
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

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)

    # Collection stats
    st.markdown('<div class="dq-section-label">Collection</div>', unsafe_allow_html=True)
    try:
        chunk_count = retrieval.get_collection_count()
    except Exception:
        chunk_count = 0
    st.markdown(f'<div class="dq-stat">{chunk_count}</div>', unsafe_allow_html=True)
    st.markdown('<div class="dq-stat-label">chunks indexed</div>', unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # Settings
    st.markdown('<div class="dq-section-label">Settings</div>', unsafe_allow_html=True)
    top_k = st.slider("", min_value=1, max_value=10, value=config.TOP_K, label_visibility="collapsed")
    st.markdown('<div class="dq-stat-label">retrieval depth</div>', unsafe_allow_html=True)

# Main Area
st.markdown('<div class="dq-main-header">DocuQuery</div>', unsafe_allow_html=True)
st.markdown('<div class="dq-main-sub">Ask questions grounded in your company documents</div>', unsafe_allow_html=True)

# Empty state (shown when no messages yet)
if not st.session_state.messages:
    st.markdown("""
    <div style='text-align:center; padding: 4rem 0; color: #2A2A2A;'>
        <div style='font-size:2rem; margin-bottom:0.5rem;'>↑</div>
        <div style='font-size:0.875rem;'>Upload and ingest documents to begin</div>
    </div>
    """, unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "sources" in message:
            sources = message["sources"]
            with st.expander(f"· {len(sources)} sources retrieved"):
                for chunk in sources:
                    st.markdown(f"**{chunk['source']}** · page {chunk['page']} · score {chunk['score']:.2f}")
                    st.markdown(f"<div style='font-size:0.8rem; color:#555; margin-top:0.25rem'>{chunk['content'][:200]}...</div>", unsafe_allow_html=True)
                    st.markdown("---")

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
                with st.expander(f"· {len(sources)} sources retrieved"):
                    for chunk in sources:
                        st.markdown(f"**{chunk['source']}** · page {chunk['page']} · score {chunk['score']:.2f}")
                        st.markdown(f"<div style='font-size:0.8rem; color:#555; margin-top:0.25rem'>{chunk['content'][:200]}...</div>", unsafe_allow_html=True)
                        st.markdown("---")
            
            # Save to history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response_text,
                "sources": sources
            })
