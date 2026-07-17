import os
import json
from typing import List
from pydantic import BaseModel, Field
from groq import Groq
from src.rag.database import retrieve_context
from src.utils.config import FALLBACK_MODELS, QUIZ_MAX_TOKENS

# Define the structured output format using Pydantic
class QuizOption(BaseModel):
    label: str = Field(description="Opsi jawaban (A/B/C/D)")
    text: str = Field(description="Teks pilihan jawaban")

class QuizQuestion(BaseModel):
    question: str = Field(description="Pertanyaan kuis")
    options: List[QuizOption] = Field(description="Daftar 4 pilihan jawaban")
    correct_answer: str = Field(description="Kunci jawaban yang benar (A/B/C/D)")
    explanation: str = Field(description="Penjelasan singkat mengapa jawaban tersebut benar")

class QuizData(BaseModel):
    title: str = Field(description="Judul kuis")
    questions: List[QuizQuestion] = Field(description="Daftar 5 pertanyaan kuis")

_groq_client = None

def get_client():
    global _groq_client
    if _groq_client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY belum diisi di file .env")
        _groq_client = Groq(api_key=api_key)
    return _groq_client

def generate_quiz(topic: str) -> QuizData | str:
    """
    Generate a highly structured JSON quiz using Groq JSON mode.
    """
    context = retrieve_context(topic, top_k=5)
    
    if not context or len(context.strip()) < 20:
        return "⚠️ Guru tidak menemukan referensi materi untuk topik ini. Silakan kembali ke Langkah 1."

    system_prompt = """Kamu adalah pembuat soal kuis yang pintar.
Keluarkan hasil murni dalam format JSON (tanpa tag markdown ```json).
Skema JSON yang harus kamu ikuti adalah:
{
  "title": "Judul kuis",
  "questions": [
    {
      "question": "Pertanyaan",
      "options": [
        {"label": "A", "text": "Pilihan A"},
        {"label": "B", "text": "Pilihan B"},
        {"label": "C", "text": "Pilihan C"},
        {"label": "D", "text": "Pilihan D"}
      ],
      "correct_answer": "A",
      "explanation": "Penjelasan"
    }
  ]
}
"""

    user_prompt = f"""Buatkan 5 soal pilihan ganda (A, B, C, D) tentang "{topic}".
SOAL HARUS MURNI BERDASARKAN MATERI BERIKUT:

[Materi Buku]
{context}
"""

    client = get_client()
    last_error = None
    
    for model_name in FALLBACK_MODELS:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_completion_tokens=QUIZ_MAX_TOKENS,
                response_format={"type": "json_object"},
            )
            
            # Parsing the JSON string into Pydantic model
            json_str = response.choices[0].message.content
            return QuizData.model_validate_json(json_str)
            
        except Exception as e:
            last_error = str(e)
            continue
            
    return f"Gagal membuat kuis setelah mencoba semua model Groq. Error terakhir: {last_error}"
