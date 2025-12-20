
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.core.logger import logger
from app.dependencies import get_scam_analyzer
from app.services.audio.debug_service import DeepgramDebugService
from app.services.intelligence import IntelligenceAnalyzer
from app.services.intelligence.models import RiskLevel

router = APIRouter()

@router.post("/audio")
async def debug_audio_endpoint(
    file: UploadFile = File(...),
    analyzer: IntelligenceAnalyzer = Depends(get_scam_analyzer),
):
    """
    Debug endpoint to upload an audio file, transcribe it, and run scam detection.
    """
    logger.info("debug_audio_upload_received", filename=file.filename)
    
    try:
        # 1. Read the uploaded file
        content = await file.read()
        
        # 2. Transcribe using the debug service
        debug_service = DeepgramDebugService()
        transcript = await debug_service.transcribe(content)
        
        logger.info("debug_transcript_generated", transcript=transcript)
        
        # 3. Analyze the transcript
        decision = await analyzer.analyze(transcript)
        
        # 4. Construct response
        response = {
            "transcript": transcript,
            "risk_assessment": {
                "risk_level": decision.risk.value,
                "reason": decision.reason,
                "suggested_action": decision.action.value
            },
            "alert_simulated": decision.risk == RiskLevel.HIGH
        }
        
        if decision.risk == RiskLevel.HIGH:
            logger.warning("debug_scam_detected", reason=decision.reason)
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error("debug_endpoint_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e
