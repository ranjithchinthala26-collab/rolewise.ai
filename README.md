# RoleWise AI – Resume-Based Technical Interview Platform

## Overview

RoleWise AI is a web application that helps candidates prepare for technical interviews based on their resumes and selected job roles.

Candidates can upload their resumes, choose an interview role, answer technical questions, and receive feedback through a final interview report.

## Features

- Upload resumes in PDF or TXT format.
- Extract candidate information and technical skills.
- Select from four interview roles: AI/ML Engineer, Backend Engineer, Python Developer, and Full Stack Developer.
- Generate interview questions based on resume details and selected roles.
- Retrieve relevant information from a local knowledge base using RAG.
- Conduct a six-question technical interview.
- Store interview answers and evaluation feedback.
- Generate a final report with scores, strengths, and improvement areas.

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | React.js, Vite |
| Backend | Python, FastAPI |
| Database | SQLite, SQLAlchemy |
| Vector Database | ChromaDB |
| Embeddings | Sentence Transformers |
| AI Integration | OpenAI API (Optional) |
| Deployment | Docker, Docker Compose |

## Project Structure

```text
RoleWise-AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── data/
│   │   └── knowledge_base/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── docs/
├── scripts/
├── docker-compose.yml
└── README.md
```

## Installation and Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd RoleWise-AI
```

### 2. Run the backend

```bash
cd backend
python -m venv venv
```

Activate the environment:

**Windows:**
```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies and start the server:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend URL: http://localhost:8000

API Documentation: http://localhost:8000/docs

### 3. Run the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: http://localhost:5173

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check server status |
| GET | `/api/roles` | Get available interview roles |
| POST | `/api/knowledge/ingest` | Index knowledge-base documents |
| POST | `/api/sessions` | Upload resume and create session |
| POST | `/api/sessions/{id}/start` | Start interview |
| POST | `/api/sessions/{id}/answer` | Submit an answer |
| GET | `/api/sessions/{id}/report` | Get final interview report |

## How It Works

1. The candidate uploads a resume and selects an interview role.
2. The backend extracts resume information and identifies relevant skills.
3. The interview service prepares questions using the resume and selected role.
4. Relevant content is retrieved from the local knowledge base using ChromaDB.
5. The candidate answers the generated technical questions.
6. Answers and feedback are stored in SQLite.
7. A final report is generated with scores and improvement areas.

## Run Tests

From the backend directory:

```bash
python -m pytest -q
```

## Future Improvements

- Improve resume parsing and skill extraction.
- Add more technical interview roles.
- Improve answer evaluation with structured scoring.
- Add user authentication and interview history.
- Deploy the application with cloud-based storage.

## Note

The application supports an optional OpenAI API integration. Without an API key, it uses local fallback logic for question generation and evaluation.

The included knowledge-base files are starter notes. Add and index the assignment's permitted reference book before claiming book-based retrieval.

## License

Developed for educational and technical assessment purposes.