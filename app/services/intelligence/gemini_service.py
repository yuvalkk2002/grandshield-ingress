import asyncio
import json

import google.generativeai as genai

from app.config import settings
from app.core.exceptions import ConfigurationError, ExternalServiceError
from app.core.logger import logger

from .base import IntelligenceAnalyzer
from .models import AnalysisResult, AnalyzedAction, RiskLevel

# TODO - rewrite with pydanticAI and agnostic model-prompt pair.

class GeminiScamAnalyzer(IntelligenceAnalyzer):
    """
    Implementation of IntelligenceAnalyzer using Google's Gemini.
    Maintain state (chat history) for the duration of its life.
    """

    def __init__(self):
        if not settings.GOOGLE_API_KEY:
             raise ConfigurationError("Google/Gemini API key is missing configuration")

        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.chat = self.model.start_chat(history=[])
            self.system_prompt = """
            Analyze this call transcript for scam indicators (urgency, bank details, fear).
            Return ONLY JSON: {"risk": "LOW"|"HIGH", "reason": "string", "action": "NONE"|"ALERT"}
            """
        except Exception as e:
            logger.error("gemini_init_failed", error=str(e))
            raise ExternalServiceError("Failed to initialize Gemini service", original_error=e) from e

    async def analyze(self, text: str) -> AnalysisResult:
        try:
            # Note: generativeai.chat.send_message is synchronous blocking in many versions.
            # Run blocking call in a thread executor
            loop = asyncio.get_running_loop()
            
            # We append the system prompt instructions to reinforce the desired output format
            # In a real chat, we might use system instructions in the model config if supported,
            # or just prepend to the first message. Here we append to every message to ensure strict compliance.
            message = f"{self.system_prompt} \n Transcript Chunk: {text}"
            
            response = await loop.run_in_executor(
                None, 
                lambda: self.chat.send_message(message)
            )
            
            # Check for block filtering or empty response
            if not response.text:
                logger.warning("gemini_empty_response")
                return AnalysisResult(risk=RiskLevel.LOW, reason="Empty response from AI", action=AnalyzedAction.NONE)

            # Basic cleaning to ensure JSON
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            
            try:
                data = json.loads(clean_json)
                result = AnalysisResult(
                    risk=RiskLevel(data.get("risk", "LOW")),
                    reason=data.get("reason", "Unknown"),
                    action=AnalyzedAction(data.get("action", "NONE"))
                )
            except (json.JSONDecodeError, ValueError) as ve:
                logger.warning("gemini_response_parse_error", raw=clean_json, error=str(ve))
                # Fallback
                result = AnalysisResult(risk=RiskLevel.LOW, reason="Failed to parse analysis", action=AnalyzedAction.NONE)

            logger.info("analysis_complete", result=result.model_dump())
            return result

        except Exception as e:
            logger.error("analysis_failed", error=str(e))
            # We explicitly return a safe default instead of crashing the websocket loop
            return AnalysisResult(risk=RiskLevel.LOW, reason=f"Analysis failed: {str(e)}", action=AnalyzedAction.NONE)
