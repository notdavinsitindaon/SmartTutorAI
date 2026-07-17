from src.utils.config import EMBEDDING_MODEL

_model = None

def get_embedding_model():
    """
    Load SentenceTransformer model with local-first strategy (Singleton).
    """
    global _model
    if _model is not None:
        return _model

    from sentence_transformers import SentenceTransformer

    try:
        _model = SentenceTransformer(EMBEDDING_MODEL, local_files_only=True)
    except Exception:
        _model = SentenceTransformer(EMBEDDING_MODEL)

    return _model

def create_embeddings(chunks):
    model = get_embedding_model()
    embeddings = model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )
    return embeddings.tolist()
