from typing import Type

from app.services.alerts import AlertService, LoggingAlertService
from app.services.audio import AudioStreamer, DeepgramStreamer
from app.services.intelligence import GeminiScamAnalyzer, IntelligenceAnalyzer


def get_scam_analyzer() -> IntelligenceAnalyzer:
    """
    Returns a new instance of the scam analyzer.
    Crucial to avoid sharing chat history between different calls.
    """
    return GeminiScamAnalyzer()


def get_audio_streamer_cls() -> Type[AudioStreamer]:
    """
    Returns the class to be used for audio streaming.
    This allows swapping the implementation (e.g., config-based) without changing client code.
    """
    return DeepgramStreamer


def get_alert_service() -> AlertService:
    """
    Returns an instance of the alert service.
    """
    return LoggingAlertService()

