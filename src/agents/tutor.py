import os
import time
from groq import Groq
from src.rag.database import retrieve_context
from src.utils.config import FALLBACK_MODELS, TEMPERATURE, MAX_TOKENS

SYSTEM_PROMPT = """Kamu adalah "Guru Pintar", pendamping belajar yang sangat ramah, hangat, dan sabar.

Aturan Utama:
1. Sapa murid dengan ramah (misal: "Halo!", "Mari kita bahas!").
2. Jawab pertanyaan MENGUTAMAKAN informasi dari [Materi Utama Buku].
3. Jika pertanyaan bersifat UMUM dan tidak ada di buku (contoh: kapan merdeka, apa itu SEO), gunakan [Pencarian Internet Cepat] untuk menjawabnya secara faktual.
4. Jangan mengarang informasi dari luar konteks yang diberikan di bawah.
5. Jelaskan dengan bahasa Indonesia yang sederhana dan mudah dipahami, layaknya berbicara dengan murid sekolah.
6. Gunakan poin-poin agar mudah dibaca."""

_groq_client = None

def get_client():
    global _groq_client
    if _groq_client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY belum diisi di file .env")
        _groq_client = Groq(api_key=api_key)
    return _groq_client

def answer_question(question: str, history: list = None):
    """
    Stream answers directly using Groq SDK, with conversation memory.
    """
    if history is None:
        history = []
        
    context = retrieve_context(question)
    
    from src.agents.curator import quick_web_search
    web_context = quick_web_search(question, max_results=5)

    if (not context or len(context.strip()) < 20) and not web_context:
        yield "⚠️ Hmm.. guru tidak bisa menemukan jawaban dari buku maupun internet. Yuk, coba tanyakan hal lain!"
        return

    prompt = f"""[Materi Utama Buku]
{context}

[Pencarian Internet Cepat]
{web_context}

[Pertanyaan Murid]
{question}
"""

    client = get_client()
    last_error = None
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": prompt})
    
    for model_name in FALLBACK_MODELS:
        try:
            got_response = False
            stream = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=TEMPERATURE,
                max_completion_tokens=MAX_TOKENS,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    got_response = True
                    yield chunk.choices[0].delta.content
            
            if got_response:
                return
                
        except Exception as e:
            last_error = str(e)
            if not got_response:
                continue
            else:
                yield f"\n\n*(Sinyal guru terputus di tengah jalan: {last_error})*"
                return
                
    yield f"\n\n*(Wah, maaf ya. Semua sinyal otak AI sedang sibuk atau ditolak. Error terakhir: {last_error})*"
