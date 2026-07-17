import os
import re
from tavily import TavilyClient
from bs4 import BeautifulSoup
from src.utils.config import CHUNK_SIZE, CHUNK_OVERLAP

_tavily_client = None

def get_tavily_client():
    global _tavily_client
    if _tavily_client is None:
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY belum diisi di file .env")
        _tavily_client = TavilyClient(api_key=api_key)
    return _tavily_client

def clean_text(text: str) -> str:
    """Removes HTML tags and excess whitespace."""
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    clean = soup.get_text(separator=" ")
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def split_text(text: str) -> list[str]:
    """Splits text into overlapping chunks."""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk = " ".join(words[i : i + CHUNK_SIZE])
        if chunk:
            chunks.append(chunk)
    return chunks

def search_and_chunk(topic: str) -> list[str]:
    """
    Search Tavily, extract raw content, clean it, and chunk it.
    """
    client = get_tavily_client()
    
    # Force trusted academic/news domains in Indonesian
    trusted_query = f"{topic} (site:.ac.id OR site:.edu OR site:.go.id OR jurnal OR berita terpercaya)"
    
    response = client.search(
        query=trusted_query,
        max_results=3,
        search_depth="basic",
        include_raw_content=True
    )
    
    results = response.get("results", [])
    all_chunks = []
    
    for res in results:
        raw = res.get('raw_content') or res.get('content', '')
        if raw and len(raw) > 200:
            cleaned = clean_text(raw)
            chunks = split_text(cleaned)
            all_chunks.extend(chunks)
            
    return all_chunks

def quick_web_search(query: str, max_results: int = 5) -> str:
    """
    Perform a fast web search to get general knowledge snippets for the Tutor.
    """
    client = get_tavily_client()
    try:
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="basic"
        )
        results = response.get("results", [])
        if not results:
            return ""
            
        formatted_snippets = []
        for i, res in enumerate(results, start=1):
            title = res.get("title", "Sumber Internet")
            content = res.get("content", "")
            formatted_snippets.append(f"[{i}] {title}: {content}")
            
        return "\n".join(formatted_snippets)
    except Exception:
        return ""
