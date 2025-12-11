from abc import ABC, abstractmethod

from .models import AnalysisResult


class IntelligenceAnalyzer(ABC):
    """
    Abstract base class for intelligence/scam analysis services.
    """

    @abstractmethod
    async def analyze(self, text: str) -> AnalysisResult:
        """
        Analyze the given text for potential scams.
        """
        pass
