class GrandShieldError(Exception):
    """Base exception for GrandShield Backend"""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error

class AudioServiceError(GrandShieldError):
    """Raised when there are issues with the audio service (e.g. Deepgram)"""
    pass

class ConfigurationError(GrandShieldError):
    """Raised when there is a configuration issue (e.g. missing secrets)"""
    pass

class ExternalServiceError(GrandShieldError):
    """Raised when a call to an external service fails"""
    pass
