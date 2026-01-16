from pydantic import BaseModel
from typing import Dict
from datetime import datetime


class ForensicDetails(BaseModel):
    facialAnalysis: int
    temporalConsistency: int
    artifactDetection: int
    metadataAnalysis: int


class EngineInfo(BaseModel):
    primary: str
    secondary: str


class PredictResponse(BaseModel):
    verdict: str
    confidence: float
    fileName: str
    fileType: str
    analyzedAt: datetime
    details: ForensicDetails
    engine: EngineInfo
