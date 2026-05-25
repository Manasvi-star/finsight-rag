import os
from typing import List, Dict, Any, AsyncGenerator
from anthropic import AsyncAnthropic
from backend.app.core.config import settings
from backend.app.services.generation.streaming import format_sse_token, format_sse_final

# Lazy initialized client
_client = None

def get_anthropic_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        api_key = settings.ANTHROPIC_API_KEY or "dummy-key"
        _client = AsyncAnthropic(api_key=api_key)
    return _client


async def generate_rag_stream(
    question: str, 
    chunks: List[Dict[str, Any]], 
    history: List[Dict[str, Any]] = None
) -> AsyncGenerator[str, None]:
    """
    Asynchronously retrieves RAG tokens from Claude and yields them as SSE events.
    At the end, yields the final event containing answer compilation, sources, and sentiment.
    """
    history = history or []
    
    # 1. Format Context
    context_str = ""
    sources = []
    for idx, chunk in enumerate(chunks):
        page = chunk.get("page") or chunk.get("metadata", {}).get("page", 0)
        source = chunk.get("source") or chunk.get("metadata", {}).get("source", "Unknown")
        text = chunk.get("text", "")
        
        context_str += f"Source [{idx + 1}] (Page {page}, File: {source}):\n{text}\n\n"
        sources.append({
            "page": page,
            "text": text
        })

    # 2. Formulate Prompt
    system_prompt = (
        "You are FinSight, a premium financial analysis AI assistant.\n"
        "You are provided with key excerpts (context) from a company's annual report.\n"
        "Answer the user's question using ONLY the provided context.\n"
        "Strictly adhere to the following rules:\n"
        "1. Do not assume or extrapolate. If the context doesn't contain the answer, say 'I do not have enough information to answer based on the provided documents.'\n"
        "2. Do not use outside knowledge.\n"
        "3. Cite the page numbers in your text when referencing a point (e.g. '[Page 5]').\n"
    )

    messages = []
    
    # Add history
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ["user", "assistant"]:
            messages.append({"role": role, "content": content})

    user_content = (
        f"<context>\n{context_str}</context>\n\n"
        f"Question: {question}"
    )
    messages.append({"role": "user", "content": user_content})

    full_answer = ""
    
    # Fallback to mock streaming if Anthropic API key is not present or is dummy
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "dummy-key":
        mock_response = (
            f"Based on the provided financial documents (citing sources):\n"
            f"This is a simulated response answering: '{question}'.\n"
            f"The annual report pages contains mentions of business segment performance.\n"
            f"Sources cited: Page 1 and Page 2."
        )
        # Stream word by word
        import asyncio
        words = mock_response.split(" ")
        for word in words:
            token = word + " "
            full_answer += token
            yield format_sse_token(token)
            await asyncio.sleep(0.05)
            
        # Get sentiment
        from backend.app.services.analysis.sentiment import sentiment_service
        sentiment_res = sentiment_service.analyze_text(full_answer)
        
        yield format_sse_final(full_answer, sources, sentiment_res)
        return

    # Call Anthropic API
    client = get_anthropic_client()
    try:
        async with client.messages.stream(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=1024,
            temperature=0.0,
            system=system_prompt,
            messages=messages
        ) as stream:
            async for event in stream:
                if event.type == "text":
                    token = event.text
                    full_answer += token
                    yield format_sse_token(token)
                    
        # Once stream completes, perform sentiment analysis on the completed answer using FinBERT
        from backend.app.services.analysis.sentiment import sentiment_service
        sentiment_res = sentiment_service.analyze_text(full_answer)
        
        yield format_sse_final(full_answer, sources, sentiment_res)

    except Exception as e:
        # Fallback error response
        error_msg = f"\n[Error generating response: {str(e)}]"
        yield format_sse_token(error_msg)
        yield format_sse_final(
            answer=full_answer + error_msg,
            sources=sources,
            sentiment={"label": "Neutral", "score": 1.0}
        )
