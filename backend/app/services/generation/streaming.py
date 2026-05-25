import json
from typing import Dict, Any, List

def format_sse_token(token: str) -> str:
    """
    Formats a single token as an SSE data event.
    """
    data = json.dumps({"token": token})
    return f"data: {data}\n\n"

def format_sse_final(answer: str, sources: List[Dict[str, Any]], sentiment: Dict[str, Any]) -> str:
    """
    Formats the final summary event containing the full answer, source list, and sentiment analysis.
    """
    data = json.dumps({
        "answer": answer,
        "sources": sources,
        "sentiment": sentiment
    })
    return f"data: {data}\n\n"
