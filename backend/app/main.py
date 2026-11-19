import json, uuid
from pathlib import Path
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.config import settings
from app.db.database import Base, engine, get_db
from app.models.entities import InterviewSession, InterviewQuestion, InterviewReport
from app.schemas.interview import SessionCreated, AnswerRequest, AnswerOut, QuestionOut, ReportOut
from app.services.resume import extract_text, extract_skills, extract_candidate_name
from app.services.interview import engine as interview_engine
from app.services.rag import rag

Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.app_name, version="1.0.0", description="Resume-aware, RAG-grounded technical interview practice platform")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_origin,
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "https://rolewise-ai-seven.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ROLES = ["Backend Engineer", "AI/ML Engineer", "Python Developer", "Full Stack Developer"]
TOTAL_QUESTIONS = 6

@app.on_event("startup")
def startup_ingestion():
    try:
        if rag.collection.count() == 0:
            rag.ingest_directory()
    except Exception as exc:
        # API remains available; ingestion can be retried using the admin endpoint.
        print(f"Knowledge-base startup ingestion skipped: {exc}")

@app.get("/api/health")
def health():
    return {"status": "ok", "service": settings.app_name}

@app.get("/api/roles")
def roles():
    return {"roles": ROLES, "question_count": TOTAL_QUESTIONS}

@app.post("/api/knowledge/ingest")
def ingest_knowledge(db: Session = Depends(get_db)):
    try:
        count = rag.ingest_directory()
        return {"chunks_indexed": count, "collection_count": rag.collection.count()}
    except Exception as exc:
        raise HTTPException(500, f"Knowledge ingestion failed: {str(exc)}")

@app.post("/api/sessions", response_model=SessionCreated)
async def create_session(role: str = Form(...), resume: UploadFile = File(...), db: Session = Depends(get_db)):
    if role not in ROLES:
        raise HTTPException(400, "Please select a supported role.")
    suffix = Path(resume.filename or "").suffix.lower()
    if suffix not in {".pdf", ".txt", ".md"}:
        raise HTTPException(400, "Upload a PDF or text resume.")
    content = await resume.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"Resume exceeds {settings.max_upload_mb} MB.")
    try:
        text = extract_text(resume.filename or "resume.pdf", content)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    skills = extract_skills(text)
    candidate = extract_candidate_name(text)
    session_id = str(uuid.uuid4())
    record = InterviewSession(id=session_id, candidate_name=candidate, role=role, resume_text=text, skills_json=json.dumps(skills), status="created")
    db.add(record); db.commit()
    return SessionCreated(session_id=session_id, candidate_name=candidate, role=role, skills=skills, message="Resume processed. Start the interview when you are ready.")

def _make_question(db: Session, session: InterviewSession, index: int) -> InterviewQuestion:
    previous = db.scalars(select(InterviewQuestion).where(InterviewQuestion.session_id == session.id).order_by(InterviewQuestion.id)).all()
    answers = [q.answer_text for q in previous if q.answer_text]
    skills = json.loads(session.skills_json or "[]")
    retrieval_query = interview_engine.make_query(session.role, skills, session.resume_text, answers, index)
    question, topic, difficulty, retrieved = interview_engine.generate_question(session.role, skills, session.resume_text, answers, index)
    traceable_context = "\n\n".join(f"[Source: {item['source']} | relevance: {item['relevance']}]\n{item['text']}" for item in retrieved)
    record = InterviewQuestion(session_id=session.id, question_text=question, topic=topic, difficulty=difficulty,
                               retrieved_context=traceable_context, retrieval_query=retrieval_query,
                               feedback="", answer_text="")
    db.add(record); db.commit(); db.refresh(record)
    return record

def _question_out(q: InterviewQuestion, number: int):
    return QuestionOut(question_id=q.id, question=q.question_text, topic=q.topic, difficulty=q.difficulty,
                       question_number=number, total_questions=TOTAL_QUESTIONS)

@app.post("/api/sessions/{session_id}/start", response_model=QuestionOut)
def start_interview(session_id: str, db: Session = Depends(get_db)):
    session = db.get(InterviewSession, session_id)
    if not session: raise HTTPException(404, "Interview session not found.")
    if session.status == "completed": raise HTTPException(409, "This interview is already completed.")
    existing_questions = db.scalars(select(InterviewQuestion).where(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.id)).all()
    if existing_questions:
        current = next((q for q in existing_questions if not q.answer_text), existing_questions[-1])
        return _question_out(current, existing_questions.index(current) + 1)
    session.status = "in_progress"; db.commit()
    return _question_out(_make_question(db, session, 0), 1)

@app.post("/api/sessions/{session_id}/answer", response_model=AnswerOut)
def submit_answer(session_id: str, payload: AnswerRequest, db: Session = Depends(get_db)):
    session = db.get(InterviewSession, session_id)
    if not session: raise HTTPException(404, "Interview session not found.")
    if session.status == "completed": raise HTTPException(409, "This interview is already completed.")
    questions = db.scalars(select(InterviewQuestion).where(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.id)).all()
    current = next((q for q in questions if not q.answer_text), None)
    if current is None: raise HTTPException(409, "No unanswered question is available. Start or refresh the interview.")
    current.answer_text = payload.answer.strip()
    score, feedback = interview_engine.evaluate_answer(current.question_text, current.answer_text, current.retrieved_context)
    current.score = score; current.feedback = feedback; db.commit()
    answered_count = sum(1 for q in questions if q.answer_text)
    if answered_count >= TOTAL_QUESTIONS:
        session.status = "completed"; db.commit()
        _build_report(db, session)
        return AnswerOut(saved=True, feedback=feedback, score=score, completed=True)
    next_q = _make_question(db, session, answered_count)
    return AnswerOut(saved=True, feedback=feedback, score=score, next_question=_question_out(next_q, answered_count + 1), completed=False)

def _build_report(db: Session, session: InterviewSession):
    qs = db.scalars(select(InterviewQuestion).where(InterviewQuestion.session_id == session.id).order_by(InterviewQuestion.id)).all()
    scored = [q.score for q in qs if q.score is not None]
    avg = round(sum(scored) / len(scored), 1) if scored else 0
    strengths, improvements = [], []
    if avg >= 7: strengths.append("Consistent understanding across the interview topics")
    if any(len((q.answer_text or "").split()) >= 45 for q in qs): strengths.append("Able to explain ideas with supporting detail")
    if any((q.score or 0) < 5 for q in qs): improvements.append("Review the lower-scoring concepts and practise explaining them step by step")
    if not strengths: strengths.append("Completed the full interview and provided responses for review")
    if not improvements: improvements.append("Add concrete project examples, trade-offs, and validation steps to make strong answers more convincing")
    summary = f"{session.candidate_name} completed a {session.role} practice interview with {len(qs)} questions. The average response score was {avg}/10. Scores are indicative practice feedback, not a hiring decision."
    report = db.query(InterviewReport).filter_by(session_id=session.id).first()
    if report:
        report.summary=summary; report.average_score=avg; report.strengths_json=json.dumps(strengths); report.improvements_json=json.dumps(improvements)
    else:
        db.add(InterviewReport(session_id=session.id, summary=summary, average_score=avg, strengths_json=json.dumps(strengths), improvements_json=json.dumps(improvements)))
    db.commit()

@app.get("/api/sessions/{session_id}/report", response_model=ReportOut)
def get_report(session_id: str, db: Session = Depends(get_db)):
    session = db.get(InterviewSession, session_id)
    if not session: raise HTTPException(404, "Interview session not found.")
    if session.status != "completed": raise HTTPException(409, "Complete the interview to view the report.")
    report = db.query(InterviewReport).filter_by(session_id=session_id).first()
    qs = db.scalars(select(InterviewQuestion).where(InterviewQuestion.session_id == session_id).order_by(InterviewQuestion.id)).all()
    transcript = [{"question": q.question_text, "topic": q.topic, "difficulty": q.difficulty, "answer": q.answer_text,
                   "score": q.score, "feedback": q.feedback} for q in qs]
    return ReportOut(session_id=session_id, candidate_name=session.candidate_name, role=session.role,
                     total_questions=len(qs), answered_questions=sum(bool(q.answer_text) for q in qs),
                     average_score=report.average_score if report else 0, summary=report.summary if report else "",
                     strengths=json.loads(report.strengths_json) if report else [],
                     improvements=json.loads(report.improvements_json) if report else [], transcript=transcript)
