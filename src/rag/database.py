import os
import uuid
import chromadb
from src.rag.embedding import get_embedding_model
from src.utils.config import MAX_CONTEXT_CHARS

_client = None
_collection = None

# HF Spaces: app directory is read-only, use /tmp instead
_db_path = "/tmp/vectordb" if os.environ.get("SPACE_ID") else "vectordb"

def _init_db():
    global _client, _collection
    _client = chromadb.PersistentClient(path=_db_path)
    _collection = _client.get_or_create_collection(name="smart_tutor")

def clear_database():
    """Clear all existing documents from the vector database."""
    global _client, _collection
    if _client is None:
        _init_db()
    
    try:
        _client.delete_collection("smart_tutor")
    except ValueError:
        pass
        
    _collection = _client.create_collection("smart_tutor")

def add_documents(chunks, embeddings):
    if _collection is None:
        _init_db()
        
    ids = [str(uuid.uuid4()) for _ in chunks]
    _collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings
    )

def retrieve_context(query, top_k=3):
    """Retrieve top-k most relevant chunks, capped by max character limit."""
    if _collection is None:
        _init_db()
        
    model = get_embedding_model()
    
    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    result = _collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    if not result["documents"] or not result["documents"][0]:
        return ""
    
    documents = result["documents"][0]
    
    context = ""
    for doc in documents:
        if len(context) + len(doc) > MAX_CONTEXT_CHARS:
            remaining = MAX_CONTEXT_CHARS - len(context)
            if remaining > 100:
                context += doc[:remaining]
            break
        context += doc + "\n\n"
    
    return context.strip()
