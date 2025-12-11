from abc import ABC, abstractmethod


class AlertService(ABC):
    """
    Abstract base class for alert services.
    """

    @abstractmethod
    async def send_alert(self, destination: str, message: str) -> bool:
        pass
