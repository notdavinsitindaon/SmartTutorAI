# 🚀 SmartTutorAI

**SmartTutorAI** adalah sebuah sistem asisten belajar (AI Tutor) interaktif yang dirancang secara khusus untuk **pengguna awam dan anak-anak**. 
Dibangun menggunakan teknologi mutakhir *Multi-Agent AI* dengan model Llama 3 (via Groq), pencarian pintar (Tavily), dan memori *Vector Database* (ChromaDB).

Sistem ini memastikan bahwa jawaban yang diberikan oleh AI selalu **Akurat, Aman, dan Berdasarkan Buku/Materi** yang disiapkan oleh orang tua/pendidik, namun tetap mampu menjawab pengetahuan umum yang mendasar. Aplikasi ini juga dilengkapi dengan Suara AI (*Edge-TTS*) untuk membacakan pertanyaan dan penjelasan.

---

## 🌟 Fitur Utama
Sistem ini terbagi ke dalam 3 langkah interaktif:
1. **📚 Langkah 1: Siapkan Materi (Kurator AI)**
   Sistem akan mencari sumber bacaan tepercaya dari internet (seperti situs berita, jurnal pendidikan, atau domain sekolah `.ac.id` / `.edu`) untuk dijadikan "Buku Pegangan" bagi Guru AI.
2. **💬 Langkah 2: Tanya Guru (Tutor AI)**
   Siswa dapat bertanya langsung kepada Guru AI. Guru hanya akan menjawab berdasarkan buku pegangan yang disiapkan di Langkah 1.
3. **🎯 Langkah 3: Uji Pemahaman (Kuis Interaktif)**
   Sistem secara otomatis akan menguji pemahaman siswa melalui kuis Pilihan Ganda Interaktif yang disertai hitungan skor dan suara *feedback* guru.

---

## 🛠️ Persyaratan Sistem
- Python 3.10 atau yang lebih baru.
- Koneksi Internet.
- **API Key Groq** (Gratis dari [console.groq.com](https://console.groq.com)).
- **API Key Tavily** (Gratis dari [tavily.com](https://tavily.com)).

---

## 📦 Cara Instalasi

1. **Unduh atau Kloning Proyek Ini**
   Buka terminal/CMD dan arahkan ke folder proyek ini.

2. **Buat File Konfigurasi Rahasia**
   Buka file `.env.example`, lalu simpan file tersebut sebagai `.env` (tanpa akhiran .example).
   Isikan API Key Anda di dalam file `.env` tersebut:
   ```env
   GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxx"
   TAVILY_API_KEY="tvly-xxxxxxxxxxxxxxxxxx"
   ```

3. **Instal Pustaka Pendukung**
   Jalankan perintah ini di dalam Terminal:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Cara Menjalankan Aplikasi

Jalankan perintah berikut di Terminal:
```bash
python app.py
```
Setelah aplikasi berjalan, buka tautan yang muncul di terminal (biasanya `http://127.0.0.1:7861`) di browser Anda (Google Chrome / Edge).

---

## 🏗️ Struktur Proyek (Arsitektur Clean Code)
- `app.py` : Tampilan antarmuka utama pengguna (Gradio UI).
- `src/agents/curator.py` : Logika untuk mencari, membersihkan, dan merangkum artikel internet.
- `src/agents/tutor.py` : Logika *chatbot* cerdas menggunakan RAG (Retrieval-Augmented Generation).
- `src/agents/quiz.py` : Logika untuk menyusun format Kuis JSON *(Structured Output)*.
- `src/rag/` : Folder pengelola *Vector Database* (ChromaDB) untuk memori AI.
- `src/utils/` : Berisi konfigurasi terpusat dan sistem pengubah Teks-ke-Suara (TTS).

---
*Dibuat untuk Masa Depan Pendidikan Indonesia.* 🇮🇩
