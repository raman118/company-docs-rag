import streamlit as st
import os
import subprocess
from src.chat import ask

st.set_page_config(page_title="DocuQuery", layout="wide")
st.title("DocuQuery — Company Knowledge Assistant")

UPLOAD_DIR = "./uploaded_docs/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

with st.sidebar:
    st.header("Document Management")
    uploaded_files = st.file_uploader(
        "Upload PDF, TXT, or MD files",
        accept_multiple_files=True,
        type=['pdf', 'txt', 'md']
    )
    if st.button("Ingest Documents"):
        if uploaded_files:
            with st.spinner("Saving files..."):
                for file in uploaded_files:
                    with open(os.path.join(UPLOAD_DIR, file.name), "wb") as f:
                        f.write(file.getbuffer())
            
            with st.spinner("Ingesting documents (this may take a while)..."):
                # Call ingest.py using subprocess. 
                # Assumes streamlit is running from the root directory as per instructions.
                result = subprocess.run(["python", "-m", "src.ingest", UPLOAD_DIR], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("Ingestion complete!")
                    with st.expander("Ingestion Logs"):
                        st.text(result.stdout)
                else:
                    st.error(f"Ingestion failed!\n\n{result.stderr}")
        else:
            st.warning("Please upload files first.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box at bottom
if prompt := st.chat_input("Ask a question about the company documents..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Retrieving and generating answer..."):
            response = ask(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
