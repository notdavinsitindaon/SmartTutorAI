import os
import json
import gradio as gr
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

# Build the UI
with gr.Blocks(title="SmartTutorAI", theme=gr.themes.Soft(primary_hue="blue", secondary_hue="indigo")) as demo:
    
    gr.HTML("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #2b3a42; font-weight: 800; margin-bottom: 0;">🚀 SmartTutorAI</h1>
        <p style="color: #6b7280; font-size: 1.1rem;">Asisten Belajar Interaktif untuk Masa Depan Pendidikan</p>
    </div>
    """)
    
    with gr.Tabs():
        # TAB 1: KURATOR (PERSIAPAN MATERI)
        with gr.TabItem("📚 Langkah 1: Siapkan Materi"):
            gr.Markdown("### 🔍 Temukan Bahan Pelajaran")
            gr.Markdown("Ketik topik yang ingin dipelajari. Kurator AI akan mencari artikel, jurnal, dan berita edukasi terpercaya untuk dijadikan bahan bacaan Guru.")
            
            with gr.Row():
                topic_input = gr.Textbox(label="Topik Pelajaran", placeholder="Contoh: Proses Terjadinya Hujan", scale=4)
                curate_btn = gr.Button("Cari & Siapkan Materi", variant="primary", scale=1)
                
            curator_status = gr.Textbox(label="Status Pencarian", lines=5, interactive=False)
            
            def process_material(topic):
                try:
                    from src.rag.database import clear_database, add_documents
                    from src.agents.curator import search_and_chunk
                    from src.rag.embedding import create_embeddings
                    
                    clear_database()
                    
                    log = [f"🔍 Sedang mencari sumber terpercaya untuk '{topic}'..."]
                    yield "\n".join(log)
                    
                    chunks = search_and_chunk(topic)
                    if not chunks:
                        log.append("❌ Gagal menemukan artikel yang memadai. Coba topik lain.")
                        yield "\n".join(log)
                        return
                    
                    log.append(f"✅ Ditemukan bahan bacaan. Sedang merangkum dan mengingat materi...")
                    yield "\n".join(log)
                    
                    embeddings = create_embeddings(chunks)
                    add_documents(chunks, embeddings)
                    
                    log.append("🎉 Selesai! Buku pelajaran sudah siap. Silakan pindah ke tab 'Langkah 2: Tanya Guru'.")
                    yield "\n".join(log)
                    
                except Exception as e:
                    yield f"Terjadi kesalahan: {str(e)}"
                    
            curate_btn.click(fn=process_material, inputs=topic_input, outputs=curator_status)
            
        # TAB 2: TUTOR (TANYA JAWAB)
        with gr.TabItem("💬 Langkah 2: Tanya Guru"):
            gr.Markdown("### 👩‍🏫 Diskusi Langsung dengan Guru Pintar")
            gr.Markdown("Guru HANYA akan menjawab berdasarkan materi yang disiapkan di Langkah 1.")
            
            def chat_stream(message, history):
                from src.agents.tutor import answer_question
                response = ""
                for chunk in answer_question(message):
                    response += chunk
                    yield response
                    
            gr.ChatInterface(fn=chat_stream)
            
        # TAB 3: KUIS (LATIHAN)
        with gr.TabItem("🎯 Langkah 3: Uji Pemahaman"):
            gr.Markdown("### 📝 Waktunya Latihan Soal!")
            
            # State rahasia untuk menyimpan data Kuis
            quiz_state = gr.State(None)
            
            with gr.Row():
                quiz_topic = gr.Textbox(label="Topik Kuis", placeholder="Contoh: Soal Hujan", scale=4)
                quiz_btn = gr.Button("Buat Kuis & Suara", variant="primary", scale=1)
                
            quiz_status = gr.Markdown(visible=False)
            quiz_audio_initial = gr.Audio(label="Suara Guru Membacakan Soal", visible=False)
            
            # Tempat menampung 5 soal secara dinamis
            q_radios = []
            for i in range(5):
                q_radios.append(gr.Radio(label=f"Soal {i+1}", choices=[], visible=False, interactive=True))
                
            submit_btn = gr.Button("Submit Jawaban", variant="secondary", visible=False)
            
            # Area Hasil
            score_display = gr.Markdown(visible=False)
            quiz_audio_result = gr.Audio(label="Suara Penjelasan Guru", visible=False)
                
            def generate_quiz_and_audio(topic):
                # 1. Tampilkan status loading SEKETIKA saat tombol diklik
                yield [
                    None, 
                    gr.update(value="⏳ *Sedang meracik kuis dan merekam suara guru... Mohon tunggu sekitar 5-10 detik.*", visible=True),
                    gr.update(visible=False)
                ] + [gr.update(visible=False)]*5 + [
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=False)
                ]
                
                # 2. Mulai proses berat
                try:
                    from src.agents.quiz import generate_quiz
                    from src.utils.tts import save_audio
                    
                    quiz_data = generate_quiz(topic)
                    if isinstance(quiz_data, str):
                        # Gagal
                        yield [None, gr.update(value=f"**Error:** {quiz_data}", visible=True), gr.update(visible=False)] + [gr.update(visible=False)]*5 + [gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)]
                        return
                    
                    # Buat teks untuk dibaca bersuara (HANYA SOAL DAN OPSI)
                    spoken_text = f"Kuis tentang {quiz_data.title}. Mari kita mulai. "
                    
                    updates = []
                    for i in range(5):
                        if i < len(quiz_data.questions):
                            q = quiz_data.questions[i]
                            # Gabungkan pertanyaan dan pilihan
                            spoken_text += f"Pertanyaan ke-{i+1}: {q.question}. "
                            choices_list = []
                            for opt in q.options:
                                spoken_text += f"Pilihan {opt.label}: {opt.text}. "
                                choices_list.append(f"{opt.label}. {opt.text}")
                            
                            updates.append(gr.update(
                                label=f"Soal {i+1}: {q.question}",
                                choices=choices_list,
                                value=None, # Reset jawaban sebelumnya
                                visible=True
                            ))
                        else:
                            updates.append(gr.update(visible=False))
                    
                    os.makedirs("audio", exist_ok=True)
                    audio_path = "audio/quiz_voice.mp3"
                    save_audio(spoken_text, audio_path)
                    
                    # Format output akhir
                    yield [
                        quiz_data.model_dump(),
                        gr.update(value=f"### 📄 {quiz_data.title}", visible=True),
                        gr.update(value=audio_path, visible=True)
                    ] + updates + [
                        gr.update(visible=True),
                        gr.update(visible=False),
                        gr.update(visible=False)
                    ]
                except Exception as e:
                    yield [None, gr.update(value=f"**Terjadi Kesalahan Sistem:** {str(e)}", visible=True), gr.update(visible=False)] + [gr.update(visible=False)]*5 + [gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)]
                
            def calculate_score(state, ans1, ans2, ans3, ans4, ans5):
                if not state:
                    return gr.update(), gr.update()
                    
                from src.utils.tts import save_audio
                
                answers = [ans1, ans2, ans3, ans4, ans5]
                score = 0
                total = len(state['questions'])
                
                spoken_result = ""
                md_result = "### Hasil Kuis Anda\n\n"
                
                for i in range(total):
                    q = state['questions'][i]
                    correct_letter = q['correct_answer']
                    user_ans = answers[i]
                    
                    user_letter = ""
                    if user_ans and len(user_ans) > 0:
                        user_letter = user_ans[0] # Ambil huruf pertamanya ("A. ...")
                        
                    is_correct = (user_letter == correct_letter)
                    if is_correct:
                        score += 1
                        md_result += f"**Soal {i+1}:** ✅ Benar! (Jawaban: {correct_letter})\n"
                        spoken_result += f"Pertanyaan {i+1}, jawaban kamu benar. "
                    else:
                        md_result += f"**Soal {i+1}:** ❌ Salah. (Jawaban Benar: {correct_letter})\n"
                        spoken_result += f"Pertanyaan {i+1}, jawaban kamu salah, yang benar adalah {correct_letter}. "
                        
                    md_result += f"> *Penjelasan: {q['explanation']}*\n\n"
                    spoken_result += f"Penjelasannya: {q['explanation']}. "
                
                final_grade = int((score / total) * 100)
                md_result = f"## Skor Akhir: {final_grade}/100\n\n" + md_result
                
                spoken_result = f"Kuis selesai! Skor akhir kamu adalah {final_grade} dari 100. " + spoken_result
                
                os.makedirs("audio", exist_ok=True)
                audio_result_path = "audio/quiz_result.mp3"
                save_audio(spoken_result, audio_result_path)
                
                return [
                    gr.update(value=md_result, visible=True),
                    gr.update(value=audio_result_path, visible=True)
                ]
                
            # Wire up "Buat Kuis"
            quiz_btn.click(
                fn=generate_quiz_and_audio, 
                inputs=quiz_topic, 
                outputs=[quiz_state, quiz_status, quiz_audio_initial] + q_radios + [submit_btn, score_display, quiz_audio_result]
            )
            
            # Wire up "Submit"
            submit_btn.click(
                fn=calculate_score,
                inputs=[quiz_state] + q_radios,
                outputs=[score_display, quiz_audio_result]
            )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7861, share=False)
