from enum import Enum

from pydantic import BaseModel


class RiskLevel(str, Enum):
    LOW = "LOW"
    HIGH = "HIGH"

class AnalyzedAction(str, Enum):
    NONE = "NONE"
    ALERT = "ALERT"

class AnalysisResult(BaseModel):
    risk: RiskLevel
    reason: str = "No significant risk detected."
    action: AnalyzedAction = AnalyzedAction.NONE
