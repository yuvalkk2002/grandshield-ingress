import asyncio
import logging

from app.core.exceptions import AudioServiceError

logger = logging.getLogger(__name__)

class DeepgramDebugService:
    """
    Implementation of audio service for debugging using Deepgram's pre-recorded API.
    """
    
    async def transcribe(self, audio_data: bytes) -> str:
        """
        Transcribes the given audio data (bytes) using Deepgram's Live API (sockets)
        to simulate the real workflow.
        Returns the transcript string.
        """
        try:
            from app.services.audio.deepgram_service import DeepgramStreamer
            
            transcript_parts = []
            
            async def collect_transcript(text: str):
                transcript_parts.append(text)
            
            streamer = DeepgramStreamer(on_transcript_callback=collect_transcript)
            
            if not await streamer.start():
                raise AudioServiceError("Failed to start Deepgram streamer for debug")
            
            # Simulate streaming by sending chunks
            chunk_size = 4096
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                await streamer.send_audio(chunk)
                # Small yield to mimic network/processing delay and allow event loop to cycle
                await asyncio.sleep(0.01) 
            
            # Stop the connection - this sends the Finish message to Deepgram
            await streamer.stop()
            
            # Give a short buffer for final messages to be processed by the callback
            # Since callbacks are fired as independent tasks
            await asyncio.sleep(0.5)
            
            return " ".join(transcript_parts)
            
        except Exception as e:
            logger.error(f"Deepgram debug transcription failed: {e}")
            raise AudioServiceError("Failed to transcribe audio for debug", original_error=e) from e
