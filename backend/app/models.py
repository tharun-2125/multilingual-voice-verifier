from sqlalchemy import Column, Integer, String, Text, DateTime
import datetime

from .database import Base

class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    original_meaning = Column(Text)
    translated_meaning = Column(Text)
    translated_main = Column(Text, nullable=True)
    target_language = Column(String, index=True)
    detected_language = Column(String, index=True)
    pipeline = Column(String, index=True, default="gemini")
    content_category = Column(String, index=True, nullable=True)
    _recommendations = Column("recommendations", Text, nullable=True)
    extracted_claim = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def translated_full(self):
        """Alias translated_meaning as translated_full for API response symmetry."""
        return self.translated_meaning

    @property
    def recommendations(self):
        import json
        if self._recommendations:
            try:
                return json.loads(self._recommendations)
            except Exception:
                return []
        return []

    @recommendations.setter
    def recommendations(self, value):
        import json
        self._recommendations = json.dumps(value if value is not None else [])


