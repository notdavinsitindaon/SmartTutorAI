import asyncio
import edge_tts

# Indonesian Neural Voices from Edge-TTS
# Female: id-ID-GadisNeural
# Male: id-ID-ArdiNeural
VOICE = "id-ID-GadisNeural"

def save_audio(text: str, output_path: str):
    """
    Synthesize speech using Microsoft Edge Neural TTS.
    Compatible with both local and Hugging Face Spaces environments.
    """
    async def _main():
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(output_path)
    
    try:
        loop = asyncio.get_running_loop()
        # Jika sudah ada event loop (HF Spaces / Gradio), gunakan nest_asyncio
        import nest_asyncio
        nest_asyncio.apply()
        loop.run_until_complete(_main())
    except RuntimeError:
        # Tidak ada event loop aktif (lokal biasa)
        asyncio.run(_main())
