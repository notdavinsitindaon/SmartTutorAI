import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

# --- Config & Initialization ---
st.set_page_config(page_title="SmartTutorAI", page_icon="🚀", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
    
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
    
if "quiz_audio_initial" not in st.session_state:
    st.session_state.quiz_audio_initial = None
    
if "quiz_audio_result" not in st.session_state:
    st.session_state.quiz_audio_result = None
    
if "quiz_score_md" not in st.session_state:
    st.session_state.quiz_score_md = None

# --- UI Header ---
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 style="color: #2b3a42; font-weight: 800; margin-bottom: 0;">🚀 SmartTutorAI</h1>
    <p style="color: #6b7280; font-size: 1.1rem;">Asisten Belajar Interaktif untuk Masa Depan Pendidikan</p>
</div>
""", unsafe_allow_html=True)

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📚 Langkah 1: Siapkan Materi", "💬 Langkah 2: Tanya Guru", "🎯 Langkah 3: Uji Pemahaman"])

# ==========================================
# TAB 1: KURATOR
# ==========================================
with tab1:
    st.markdown("### 🔍 Temukan Bahan Pelajaran")
    st.markdown("Ketik topik yang ingin dipelajari. Kurator AI akan mencari artikel, jurnal, dan berita edukasi terpercaya untuk dijadikan bahan bacaan Guru.")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        topic_input = st.text_input("Topik Pelajaran", placeholder="Contoh: Proses Terjadinya Hujan", label_visibility="collapsed")
    with col2:
        curate_btn = st.button("Cari Materi", type="primary", use_container_width=True)
        
    if curate_btn and topic_input:
        with st.status(f"Mencari sumber materi untuk '{topic_input}'...", expanded=True) as status:
            try:
                from src.rag.database import clear_database, add_documents
                from src.agents.curator import search_and_chunk
                from src.rag.embedding import create_embeddings
                
                st.write("Menghapus ingatan lama...")
                clear_database()
                
                st.write("Melakukan kurasi artikel terpercaya...")
                chunks = search_and_chunk(topic_input)
                
                if not chunks:
                    status.update(label="Gagal menemukan artikel yang memadai. Coba topik lain.", state="error")
                else:
                    st.write(f"✅ Ditemukan bahan bacaan. Sedang merangkum dan mengingat {len(chunks)} potongan materi...")
                    embeddings = create_embeddings(chunks)
                    add_documents(chunks, embeddings)
                    
                    status.update(label="🎉 Selesai! Buku pelajaran sudah siap. Silakan pindah ke tab 'Langkah 2: Tanya Guru'.", state="complete")
                    
                    # Reset memory when new topic is learned
                    st.session_state.messages = []
            except Exception as e:
                status.update(label=f"Terjadi kesalahan: {str(e)}", state="error")

# ==========================================
# TAB 2: TUTOR
# ==========================================
with tab2:
    st.markdown("### 👩‍🏫 Diskusi Langsung dengan Guru Pintar")
    st.markdown("Guru akan mengingat percakapan Anda dan menjawab berdasarkan materi di Langkah 1.")
    
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Tanyakan sesuatu ke Guru Pintar..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            from src.agents.tutor import answer_question
            
            # Use write_stream to stream the generator output
            # history excludes the current prompt (already appended above)
            history = st.session_state.messages[:-1]
            response = st.write_stream(answer_question(prompt, history))
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# ==========================================
# TAB 3: KUIS
# ==========================================
with tab3:
    st.markdown("### 📝 Waktunya Latihan Soal!")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        quiz_topic = st.text_input("Topik Kuis", placeholder="Contoh: Soal Hujan", label_visibility="collapsed")
    with col2:
        generate_btn = st.button("Buat Kuis", type="primary", use_container_width=True)
        
    if generate_btn and quiz_topic:
        with st.spinner("⏳ Sedang meracik kuis dan merekam suara guru... Mohon tunggu..."):
            try:
                from src.agents.quiz import generate_quiz
                from src.utils.tts import save_audio
                
                quiz_data = generate_quiz(quiz_topic)
                if isinstance(quiz_data, str):
                    st.error(f"Error: {quiz_data}")
                else:
                    st.session_state.quiz_data = quiz_data.model_dump()
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_score_md = None
                    st.session_state.quiz_audio_result = None
                    
                    # Generate audio
                    spoken_text = f"Kuis tentang {quiz_data.title}. Mari kita mulai. "
                    for i, q in enumerate(quiz_data.questions):
                        spoken_text += f"Pertanyaan ke-{i+1}: {q.question}. "
                        for opt in q.options:
                            spoken_text += f"Pilihan {opt.label}: {opt.text}. "
                            
                    audio_dir = os.path.join(tempfile.gettempdir(), "audio")
                    os.makedirs(audio_dir, exist_ok=True)
                    audio_path = os.path.join(audio_dir, "quiz_voice.mp3")
                    save_audio(spoken_text, audio_path)
                    
                    st.session_state.quiz_audio_initial = audio_path
                    
            except Exception as e:
                st.error(f"Terjadi Kesalahan: {str(e)}")
                
    # Display Quiz if data exists
    if st.session_state.quiz_data:
        st.markdown(f"### 📄 {st.session_state.quiz_data['title']}")
        
        if st.session_state.quiz_audio_initial:
            st.audio(st.session_state.quiz_audio_initial)
            
        with st.form("quiz_form"):
            user_answers = []
            for i, q in enumerate(st.session_state.quiz_data['questions']):
                options = [f"{opt['label']}. {opt['text']}" for opt in q['options']]
                ans = st.radio(f"**Soal {i+1}: {q['question']}**", options=options, index=None, key=f"q_{i}")
                user_answers.append(ans)
                
            submit_quiz = st.form_submit_button("Submit Jawaban", type="primary")
            
        if submit_quiz:
            from src.utils.tts import save_audio
            st.session_state.quiz_submitted = True
            
            score = 0
            total = len(st.session_state.quiz_data['questions'])
            spoken_result = ""
            md_result = "### Hasil Kuis Anda\n\n"
            
            for i in range(total):
                q = st.session_state.quiz_data['questions'][i]
                correct_letter = q['correct_answer']
                user_ans = user_answers[i]
                
                user_letter = user_ans[0] if user_ans else ""
                
                if user_letter == correct_letter:
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
            
            st.session_state.quiz_score_md = md_result
            
            audio_dir = os.path.join(tempfile.gettempdir(), "audio")
            os.makedirs(audio_dir, exist_ok=True)
            audio_result_path = os.path.join(audio_dir, "quiz_result.mp3")
            save_audio(spoken_result, audio_result_path)
            
            st.session_state.quiz_audio_result = audio_result_path
            
            st.rerun() # Refresh to show results outside the form
            
    # Display Results if submitted
    if st.session_state.quiz_submitted and st.session_state.quiz_score_md:
        st.markdown(st.session_state.quiz_score_md)
        if st.session_state.quiz_audio_result:
            st.audio(st.session_state.quiz_audio_result)
