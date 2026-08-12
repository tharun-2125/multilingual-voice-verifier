from pydantic import BaseModel
import datetime

class TranscriptionBase(BaseModel):
    filename: str
    original_meaning: str
    translated_meaning: str
    translated_full: str | None = None
    translated_main: str | None = None
    target_language: str
    detected_language: str
    pipeline: str
    content_category: str | None = None
    recommendations: list | None = None
    extracted_claim: str | None = None


class TranscriptionCreate(TranscriptionBase):
    pass

class Transcription(TranscriptionBase):
    id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True
