from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.database import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id = Column(String(36), primary_key=True)
    candidate_name = Column(String(160), default="Candidate")
    role = Column(String(80), nullable=False)
    resume_text = Column(Text, nullable=False)
    skills_json = Column(Text, default="[]")
    status = Column(String(24), default="created")
    created_at = Column(DateTime, default=datetime.utcnow)
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    report = relationship("InterviewReport", back_populates="session", uselist=False, cascade="all, delete-orphan")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    topic = Column(String(120), default="General")
    difficulty = Column(String(24), default="Intermediate")
    retrieved_context = Column(Text, default="")
    retrieval_query = Column(Text, default="")
    answer_text = Column(Text, default="")
    feedback = Column(Text, default="")
    score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("InterviewSession", back_populates="questions")

class InterviewReport(Base):
    __tablename__ = "interview_reports"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), unique=True)
    summary = Column(Text, default="")
    strengths_json = Column(Text, default="[]")
    improvements_json = Column(Text, default="[]")
    average_score = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("InterviewSession", back_populates="report")
