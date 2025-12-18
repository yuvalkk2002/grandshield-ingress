import asyncio
from typing import Awaitable, Callable, Optional

from deepgram import DeepgramClient, LiveOptions, LiveTranscriptionEvents
from deepgram.clients.live.v1 import LiveClient

from app.config import settings
from app.core.exceptions import AudioServiceError
from app.core.logger import logger
from app.services.audio.base import AudioStreamer


class DeepgramStreamer(AudioStreamer):
    """
    Implementation of AudioStreamer using Deepgram API.
    """
    
    def __init__(self, on_transcript_callback: Callable[[str], Awaitable[None]]):
        super().__init__(on_transcript_callback)
        if not settings.DEEPGRAM_API_KEY:
            raise AudioServiceError("Deepgram API key is missing configuration")
            
        self.client = DeepgramClient(settings.DEEPGRAM_API_KEY)
        self.connection: Optional[LiveClient] = None

    async def start(self) -> bool:
        """
        Initializes the connection to Deepgram.
        Returns True if successful, raises AudioServiceError otherwise.
        """
        try:
            # nova-2 is the fastest model for streaming
            options = LiveOptions(
                model="nova-2", 
                language="multi", 
                smart_format=True,
                interim_results=False, # We only want completed sentences
                utterance_end_ms="1000",
                vad_events=True,
                encoding="linear16",
                sample_rate=16000,
                channels=1
            )
            
            # Create a websocket connection to Deepgram
            self.connection = self.client.listen.live.v("1")

            def on_message(result, **kwargs):
                try:
                    # Safely access the transcript
                    if result.channel and result.channel.alternatives:
                        alternatives = result.channel.alternatives
                        if alternatives:
                            sentence = alternatives[0].transcript
                            if sentence and len(sentence.strip()) > 0:
                                asyncio.create_task(self.callback(sentence))
                except Exception as e:
                    logger.error("error_processing_transcript_callback", error=str(e))

            def on_error(error, **kwargs):
                logger.error("deepgram_error_received", error=str(error))

            self.connection.on(LiveTranscriptionEvents.Transcript, on_message)
            self.connection.on(LiveTranscriptionEvents.Error, on_error)
            
            if await self.connection.start(options) is False:
                raise AudioServiceError("Failed to initiate connection to Deepgram")
            
            logger.info("deepgram_connected_successfully")
            return True
            
        except Exception as e:
            logger.error("deepgram_connection_failed", error=str(e))
            # Clean up if partially initialized
            if self.connection:
                await self.stop()
            raise AudioServiceError("Failed to connect to Deepgram", original_error=e) from e

    async def send_audio(self, data: bytes) -> None:
        """
        sends audio chunk to deepgram
        """
        if not self.connection:
            logger.warning("attempted_send_audio_without_connection")
            return

        try:
            await self.connection.send(data)
        except Exception as e:
            logger.error("error_sending_audio_chunk", error=str(e))
            raise AudioServiceError("Failed to send audio data", original_error=e) from e

    async def stop(self) -> None:
        """
        Closes the connection.
        """
        if self.connection:
            try:
                await self.connection.finish()
                logger.info("deepgram_connection_closed")
            except Exception as e:
                logger.error("error_closing_deepgram_connection", error=str(e))
            finally:
                self.connection = None
