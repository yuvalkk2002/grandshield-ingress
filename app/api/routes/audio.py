from typing import Type

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.core.logger import logger
from app.dependencies import (
    get_alert_service,
    get_audio_streamer_cls,
    get_scam_analyzer,
)
from app.services.alerts import AlertService
from app.services.audio import AudioStreamer
from app.services.intelligence import IntelligenceAnalyzer
from app.services.intelligence.models import RiskLevel

router = APIRouter()


@router.websocket("/ws/audio")
async def audio_endpoint(
    websocket: WebSocket,
    analyzer: IntelligenceAnalyzer = Depends(get_scam_analyzer),
    streamer_cls: Type[AudioStreamer] = Depends(get_audio_streamer_cls),
    alert_service: AlertService = Depends(get_alert_service),
):
    await websocket.accept()
    logger.info("client_connected", headers=dict(websocket.headers))

    # Define what happens when we get text back
    async def process_transcript(text):
        logger.info("transcript_received", text=text)
        decision = await analyzer.analyze(text)

        if decision.risk == RiskLevel.HIGH:
            # REMEDIATION: Send Alert back to ESP32
            await websocket.send_json(
                {
                    "type": decision.action.value,
                    "payload": "SIREN_ON",
                    "reason": decision.reason
                }
            )
            # Also notify system admins
            await alert_service.send_alert(
                destination="ADMIN_CHANNEL",
                message=f"High risk scam detected! Reason: {decision.reason}"
            )
            logger.warning("scam_alert_triggered", reason=decision.reason)

    # Initialize Audio Layer
    streamer = streamer_cls(on_transcript_callback=process_transcript)
    connected = await streamer.start()
    
    if not connected:
        await websocket.close(code=1011) # Internal error
        return

    try:
        while True:
            # 1. Receive Audio from ESP32
            data = await websocket.receive_bytes()

            # 2. Forward to Deepgram
            await streamer.send_audio(data)

    except WebSocketDisconnect:
        logger.info("client_disconnected")
        await streamer.stop()
    except Exception as e:
        logger.error("unexpected_error", error=str(e))
        await websocket.close()
