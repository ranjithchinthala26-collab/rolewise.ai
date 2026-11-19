from pydantic import BaseModel, Field
from typing import List, Optional

class SessionCreated(BaseModel):
    session_id: str
    candidate_name: str
    role: str
    skills: List[str]
    message: str

class AnswerRequest(BaseModel):
    answer: str = Field(min_length=2, max_length=10000)

class QuestionOut(BaseModel):
    question_id: int
    question: str
    topic: str
    difficulty: str
    question_number: int
    total_questions: int

class AnswerOut(BaseModel):
    saved: bool
    feedback: str
    score: float
    next_question: Optional[QuestionOut] = None
    completed: bool = False

class ReportOut(BaseModel):
    session_id: str
    candidate_name: str
    role: str
    total_questions: int
    answered_questions: int
    average_score: float
    summary: str
    strengths: List[str]
    improvements: List[str]
    transcript: list
