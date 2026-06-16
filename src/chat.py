import logging
import google.generativeai as genai
from src import config, retrieval

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s — %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are DocuQuery, a company knowledge assistant. Your sole purpose is to answer questions using ONLY the information retrieved from the company's internal documents.

## Core Behavior
- Answer ONLY from the provided document chunks enclosed in <retrieved_chunks> tags.
- If the retrieved context does not contain sufficient information, respond with exactly: "I don't have enough information in the provided documents to answer this. Please consult the relevant team or check the source document directly."
- Never fabricate, infer, or extrapolate beyond what is explicitly stated in the retrieved chunks.
- Never use your training knowledge to fill gaps.

## Citation Rules
- Every factual claim must include an inline citation: [Source: <filename>, Page: <number>]
- At the end of your response, include a "## References" section listing all cited sources.

## Conflict Handling
- If two chunks contradict each other, explicitly flag it: "Note: The documents contain conflicting information on this topic."
- Do not resolve conflicts. Surface them.

## Tone
Professional, neutral, concise. No filler phrases. No apologies. No speculation.
"""

def ask(query: str, top_k: int = config.TOP_K) -> str:
    """Orchestrates the RAG flow: retrieval -> prompt construction -> generation."""
    
    # Sanitize query to prevent XML tag injection
    safe_query = query.replace("<", "&lt;").replace(">", "&gt;")
    
    # 1. Retrieval
    chunks = retrieval.retrieve(safe_query, top_k=top_k)
    
    if not chunks:
        logger.warning("No relevant chunks found. Returning fallback message.")
        return "I don't have enough information in the provided documents to answer this. Please consult the relevant team or check the source document directly."
    
    # 2. Format Context
    chunks_xml = retrieval.format_chunks_for_prompt(chunks)
    
    # 3. Configure Gemini
    if not config.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in configuration.")
        return "Error: GEMINI_API_KEY is not configured."
        
    genai.configure(api_key=config.GEMINI_API_KEY)
    
    try:
        model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT.strip()
        )
        
        prompt = f"{chunks_xml}\n\nUser Question: {safe_query}"
        
        logger.info(f"Calling {config.GEMINI_MODEL} for generation...")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=config.MAX_OUTPUT_TOKENS,
                temperature=0.0  # Zero temperature for deterministic RAG
            )
        )
        
        # Log token usage if available
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            logger.info(f"Token usage - Prompt: {usage.prompt_token_count}, Response: {usage.candidates_token_count}")
        
        return response.text

    except Exception as e:
        logger.error(f"Error during generation: {str(e)}")
        return f"Error during generation: {str(e)}"
