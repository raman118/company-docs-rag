import os
from dotenv import load_dotenv
import google.generativeai as genai
from retrieval import retrieve

load_dotenv()

SYSTEM_PROMPT = """
You are a company knowledge assistant. Your sole purpose is to answer questions using the information retrieved from the company's internal documents — which may include PDFs, FAQs, manuals, and policy files.

## Core Behavior
- Answer ONLY from the provided document chunks in the context below.
- If the retrieved context does not contain enough information to answer the question, say exactly: "I don't have enough information in the provided documents to answer this. Please consult the relevant team or check the source document directly."
- Never fabricate, infer, or extrapolate beyond what is explicitly stated in the retrieved chunks.
- Never use your general training knowledge to fill gaps. If it's not in the docs, it doesn't exist for you.

## Citation Rules
- Every factual claim must be followed by an inline citation in the format: [Source: <document_name>, Page/Section: <identifier>]
- If multiple chunks support a claim, cite all of them.
- At the end of your response, include a "References" section listing all cited sources.

## Response Format
1. Answer the question concisely and directly.
2. Use inline citations after every factual statement.
3. End with a "References" block.
4. If the question has multiple parts, address each part separately with its own citations.

## Conflict Handling
If two retrieved chunks contradict each other, explicitly flag it:
"Note: The documents contain conflicting information on this."
Do not resolve the conflict yourself.

## Tone
Professional, neutral, and concise. No filler phrases. No apologies. No speculation.
"""

def ask(query: str) -> str:
    chunks = retrieve(query)
    
    if not chunks:
        return "I don't have enough information in the provided documents to answer this. Please consult the relevant team or check the source document directly."
    
    context_blocks = []
    for i, chunk in enumerate(chunks):
        block = f"[CHUNK {i+1}]\nSource: {chunk['source']}\nSection: {chunk['page']}\nContent: {chunk['content']}"
        context_blocks.append(block)
        
    context_text = "\n\n".join(context_blocks)
    user_message = f"<retrieved_chunks>\n{context_text}\n</retrieved_chunks>\n\nQuery: {query}"
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY not found in environment. Please add it to your .env file."
        
    genai.configure(api_key=api_key)
    
    # Using gemini-1.5-pro for complex RAG tasks
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=SYSTEM_PROMPT.strip()
    )
    
    response = model.generate_content(user_message)
    
    return response.text
