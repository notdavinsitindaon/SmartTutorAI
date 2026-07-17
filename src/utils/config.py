import os

# Groq settings
FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]
TEMPERATURE = 0.2
MAX_TOKENS = 768
QUIZ_MAX_TOKENS = 1024

# Embedding / RAG settings
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3
MAX_CONTEXT_CHARS = 1500

# Suppress HuggingFace warnings
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
