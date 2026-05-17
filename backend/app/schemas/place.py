from pydantic import BaseModel
from typing import Optional, Dict

class AccessibilityScore(BaseModel):
    score: float
    status: str  # "excellent", "partial", "limited", "no_data"
    breakdown: Dict[str, bool]