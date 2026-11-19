# Suggested demo walkthrough (3–5 minutes)

**Opening (15 seconds)**  
“Hi, this is RoleWise AI, a resume-aware technical interview practice system. It combines resume parsing, role-based retrieval, question generation, persistent interview sessions, and a final feedback report.”

**Resume and role (35 seconds)**  
Choose the AI/ML Engineer role and upload a sample PDF resume. Point out the selected track and explain that the backend extracts text and identifies skills before constructing a retrieval query.

**RAG and interview (60–90 seconds)**  
Start the interview. Explain that the query includes the selected role, extracted skills, resume evidence, and previous answers. The retrieval layer searches the local ChromaDB collection built from chunked knowledge-base documents and embeddings. Answer the first question with a practical example. Submit it and show the feedback and next question.

**Persistence and report (45–60 seconds)**  
Complete the remaining questions. Open the report and show the overall practice score, strengths, areas to improve, and transcript. Explain that sessions, questions, answers, and reports are stored in SQLite.

**Architecture (30 seconds)**  
Show the project structure and `/docs` API page. Mention that OpenAI generation/evaluation is optional and configured through environment variables; the local fallback supports a no-key demo.

**Close (10 seconds)**  
“The system is designed as a practice assistant. Its scores are indicative feedback, not a hiring decision.”

Use a synthetic or consented sample resume. Do not record API keys or private candidate data.
