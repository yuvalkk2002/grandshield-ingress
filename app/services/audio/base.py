from abc import ABC, abstractmethod
from typing import Awaitable, Callable


class AudioStreamer(ABC):
    """
    Abstract base class for audio streaming services.
    """
    
    def __init__(self, on_transcript_callback: Callable[[str], Awaitable[None]]):
        self.callback = on_transcript_callback

    @abstractmethod
    async def start(self) -> bool:
        """
        Initialize and release the connection.
        """
        pass

    @abstractmethod
    async def send_audio(self, data: bytes) -> None:
        """
        Process a chunk of audio bytes.
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """
        Close the connection and cleanup resources.
        """
        pass
