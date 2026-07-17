import asyncio
import edge_tts

# Indonesian Neural Voices from Edge-TTS
# Female: id-ID-GadisNeural
# Male: id-ID-ArdiNeural
VOICE = "id-ID-GadisNeural"

def save_audio(text: str, output_path: str):
    """
    Synthesize speech using Microsoft Edge Neural TTS.
    Runs asynchronously but blocks until done.
    """
    async def _main():
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(output_path)
        
    asyncio.run(_main())
