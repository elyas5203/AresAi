from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(1024), unique=True, index=True, nullable=False)
    name = Column(String(255), index=True)
    instagram_username = Column(String(255), unique=True, index=True)

    analysis_results = relationship("AnalysisResult", back_populates="competitor")

    def __repr__(self):
        return f"<Competitor(url='{self.url}')>"

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=False)
    title = Column(String(512))
    description = Column(Text)
    keywords = Column(Text)
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())

    competitor = relationship("Competitor", back_populates="analysis_results")

    def __repr__(self):
        return f"<AnalysisResult(competitor_id={self.competitor_id}, date='{self.analysis_date}')>"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False) # To group messages by session
    role = Column(String(50), nullable=False) # "user" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Conversation(role='{self.role}', content='{self.content[:50]}...')>"
