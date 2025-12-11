from app.core.logger import logger

from .base import AlertService


class LoggingAlertService(AlertService):
    async def send_alert(self, destination: str, message: str) -> bool:
        logger.info("sending_alert", destination=destination, message=message)
        # Here we would implement real SMS/Email logic
        return True
