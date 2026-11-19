import React, { useMemo, useState } from 'react';
import { ArrowRight, BrainCircuit, BriefcaseBusiness, CheckCircle2, ChevronRight, CircleHelp, FileText, Gauge, GraduationCap, Layers3, LoaderCircle, MessageSquareText, ShieldCheck, Sparkles, UploadCloud, X } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const roles = [
  { name: 'AI/ML Engineer', detail: 'Machine learning, model evaluation, embeddings & RAG', icon: BrainCircuit },
  { name: 'Backend Engineer', detail: 'APIs, databases, architecture & reliability', icon: Layers3 },
  { name: 'Python Developer', detail: 'Python fundamentals, frameworks & testing', icon: FileText },
  { name: 'Full Stack Developer', detail: 'Frontend, APIs, data & deployment', icon: BriefcaseBusiness },
];

function App() {
  const [role, setRole] = useState('AI/ML Engineer');
  const [file, setFile] = useState(null);
  const [session, setSession] = useState(null);
  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [report, setReport] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [stage, setStage] = useState('setup');
  const [dragging, setDragging] = useState(false);
  const [uploadInfo, setUploadInfo] = useState(null);

  const progress = useMemo(() => question ? ((question.question_number - 1) / question.total_questions) * 100 : 0, [question]);
  const call = async (path, options = {}) => {
    const response = await fetch(`${API}${path}`, options);
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || 'Something went wrong. Please try again.');
    return data;
  };

  const begin = async () => {
    if (!file) { setError('Please choose your resume first.'); return; }
    setBusy(true); setError('');
    try {
      const body = new FormData(); body.append('role', role); body.append('resume', file);
      const created = await call('/api/sessions', { method: 'POST', body });
      setSession(created); setUploadInfo(created);
      const first = await call(`/api/sessions/${created.session_id}/start`, { method: 'POST' });
      setQuestion(first); setStage('interview');
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  };

  const submit = async () => {
    if (answer.trim().length < 2) { setError('Write a short answer before continuing.'); return; }
    setBusy(true); setError('');
    try {
      const result = await call(`/api/sessions/${session.session_id}/answer`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ answer }) });
      setFeedback({ text: result.feedback, score: result.score }); setAnswer('');
      if (result.completed) {
        const finalReport = await call(`/api/sessions/${session.session_id}/report`);
        setReport(finalReport); setStage('report');
      } else {
        setQuestion(result.next_question);
      }
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  };

  const reset = () => { setStage('setup'); setSession(null); setQuestion(null); setAnswer(''); setFeedback(null); setReport(null); setFile(null); setUploadInfo(null); setError(''); };
  const chooseFile = (f) => { if (f && /\.(pdf|txt|md)$/i.test(f.name)) { setFile(f); setError(''); } else setError('Please select a PDF or text file.'); };

  return <div className="app-shell">
    <header className="topbar"><a className="brand" href="#top" onClick={e => {e.preventDefault(); reset();}}><span className="brand-mark"><BrainCircuit size={21}/></span><span>rolewise<span className="brand-dot">.</span></span></a><div className="topbar-right"><span className="secure"><ShieldCheck size={14}/> Private practice session</span><span className="top-divider"/><span className="top-label">INTERVIEW STUDIO</span></div></header>
    <main id="top">
      {stage === 'setup' && <>
        <section className="hero"><div className="eyebrow"><Sparkles size={14}/> YOUR NEXT INTERVIEW STARTS HERE</div><h1>Show what you know.<br/><span>Find what to improve.</span></h1><p className="hero-copy">A focused technical interview built around your resume, your target role, and trusted learning material.</p><div className="hero-points"><span><CheckCircle2 size={15}/> Resume-aware questions</span><span><CheckCircle2 size={15}/> Role-specific knowledge</span><span><CheckCircle2 size={15}/> Actionable feedback</span></div></section>
        <section className="setup-grid"><div className="setup-main"><div className="section-heading"><div><div className="step-label">STEP 01 <span>—</span> YOUR TARGET</div><h2>Choose your interview track</h2><p>Select the role you're preparing for. Questions adapt to your background.</p></div><span className="step-count">01 / 02</span></div>
          <div className="role-grid">{roles.map(({name, detail, icon: Icon}) => <button key={name} className={`role-card ${role === name ? 'selected' : ''}`} onClick={() => setRole(name)}><span className="role-icon"><Icon size={19}/></span><span className="role-name">{name}</span><span className="role-detail">{detail}</span><span className="radio-dot">{role === name && <span/>}</span></button>)}</div>
          <div className="section-heading resume-heading"><div><div className="step-label">STEP 02 <span>—</span> YOUR BACKGROUND</div><h2>Upload your resume</h2><p>We'll identify your skills and use them to shape the conversation.</p></div><span className="step-count">02 / 02</span></div>
          <label className={`upload-zone ${dragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`} onDragOver={e => {e.preventDefault();setDragging(true);}} onDragLeave={() => setDragging(false)} onDrop={e => {e.preventDefault();setDragging(false);chooseFile(e.dataTransfer.files[0]);}}>
            <input type="file" accept=".pdf,.txt,.md" onChange={e => chooseFile(e.target.files[0])}/>
            <span className="upload-icon">{file ? <FileText size={23}/> : <UploadCloud size={24}/>}</span><span className="upload-title">{file ? file.name : 'Drop your resume here or browse'}</span><span className="upload-sub">{file ? `${(file.size / 1024).toFixed(0)} KB · Ready to process` : 'PDF or TXT · Max 10 MB'}</span>{file && <button type="button" className="remove-file" onClick={e => {e.preventDefault();setFile(null);}} aria-label="Remove file"><X size={15}/></button>}
          </label>
          {error && <div className="error-line"><CircleHelp size={15}/>{error}</div>}
          <button className="primary-button start-button" onClick={begin} disabled={busy || !file}>{busy ? <><LoaderCircle className="spin" size={17}/> Preparing your interview…</> : <>Build my interview <ArrowRight size={17}/></>}</button>
          <p className="privacy-note"><ShieldCheck size={13}/> Your resume is used only to create this practice session.</p>
        </div>
        <aside className="setup-aside"><div className="aside-card"><div className="aside-top"><span className="aside-kicker">WHAT TO EXPECT</span><span className="live-dot"/></div><h3>A conversation that<br/>starts with <em>you.</em></h3><div className="expect-list"><div><span className="expect-icon"><FileText size={17}/></span><span><b>Resume analysis</b><small>Skills, tools and experience identified</small></span></div><div><span className="expect-icon"><BrainCircuit size={17}/></span><span><b>Context-led questions</b><small>Questions grounded in relevant material</small></span></div><div><span className="expect-icon"><MessageSquareText size={17}/></span><span><b>Six-question interview</b><small>Progressive topics and difficulty</small></span></div><div><span className="expect-icon"><Gauge size={17}/></span><span><b>Personalised report</b><small>Scores, strengths and next steps</small></span></div></div><div className="aside-footer"><GraduationCap size={17}/><span>Built for learning, practice and growth.</span></div></div><div className="aside-caption">A structured practice tool — not a hiring decision.</div></aside></section>
      </>}

      {stage === 'interview' && <section className="interview-wrap"><div className="interview-top"><div><div className="step-label">LIVE SESSION <span>—</span> {session?.role?.toUpperCase()}</div><h2>Let's get into it, {session?.candidate_name?.split(' ')[0] || 'there'}.</h2><p>Take your time. Explain your thinking as clearly as you can.</p></div><div className="session-pill"><span className="live-dot"/> IN PROGRESS</div></div>
        <div className="progress-row"><span>QUESTION {question?.question_number} <i>OF {question?.total_questions}</i></span><span>{Math.round((question?.question_number || 1) / (question?.total_questions || 6) * 100)}% COMPLETE</span></div><div className="progress-track"><div style={{width: `${((question?.question_number || 1) - 1) / (question?.total_questions || 6) * 100}%`}}/></div>
        <div className="question-card"><div className="question-meta"><span className="topic-chip">{question?.topic}</span><span className="difficulty">{question?.difficulty} level</span></div><div className="question-number">0{question?.question_number}</div><h3>{question?.question}</h3><div className="question-hint"><Sparkles size={15}/> Tip: Include the reasoning behind your approach and a practical example where possible.</div></div>
        {feedback && <div className="feedback-card"><div className="feedback-score">{feedback.score}<small>/10</small></div><div><b>Previous answer feedback</b><p>{feedback.text}</p></div></div>}
        <div className="answer-area"><label htmlFor="answer">YOUR RESPONSE</label><textarea id="answer" value={answer} onChange={e => setAnswer(e.target.value)} placeholder="Write your answer here… Explain your approach, reasoning, and any examples that help demonstrate your understanding." rows={7}/><div className="answer-bottom"><span>{answer.trim().split(/\s+/).filter(Boolean).length} words · Your answer is saved when you continue</span><button className="primary-button" onClick={submit} disabled={busy || answer.trim().length < 2}>{busy ? <><LoaderCircle className="spin" size={16}/> Evaluating…</> : <>Submit answer <ChevronRight size={17}/></>}</button></div></div>
        {error && <div className="error-line"><CircleHelp size={15}/>{error}</div>}
      </section>}

      {stage === 'report' && report && <section className="report-wrap"><div className="report-header"><div><div className="step-label">SESSION COMPLETE <span>—</span> YOUR RESULTS</div><h2>Good work, {report.candidate_name.split(' ')[0]}.</h2><p>Your interview is complete. Here's a breakdown of how you did.</p></div><span className="completed-pill"><CheckCircle2 size={15}/> COMPLETED</span></div>
        <div className="report-stats"><div className="stat-card score-stat"><span>OVERALL SCORE</span><strong>{report.average_score}<small>/10</small></strong><div className="stat-foot">Practice assessment</div></div><div className="stat-card"><span>QUESTIONS ANSWERED</span><strong>{report.answered_questions}<small>/{report.total_questions}</small></strong><div className="stat-foot">Full interview completed</div></div><div className="stat-card"><span>ROLE ASSESSED</span><strong className="role-stat">{report.role}</strong><div className="stat-foot">Resume-informed interview</div></div></div>
        <div className="summary-card"><div className="summary-icon"><Sparkles size={19}/></div><div><span className="card-overline">SESSION SUMMARY</span><p>{report.summary}</p></div></div>
        <div className="insight-grid"><div className="insight-card"><div className="insight-title"><span className="insight-symbol strength"><CheckCircle2 size={17}/></span><h3>Strengths</h3></div>{report.strengths.map((s,i)=><div className="insight-line" key={i}>{s}</div>)}</div><div className="insight-card"><div className="insight-title"><span className="insight-symbol improve"><GraduationCap size={17}/></span><h3>Areas to develop</h3></div>{report.improvements.map((s,i)=><div className="insight-line" key={i}>{s}</div>)}</div></div>
        <div className="transcript-card"><div className="transcript-head"><div><span className="card-overline">YOUR INTERVIEW</span><h3>Question-by-question review</h3></div><span>{report.transcript.length} RESPONSES</span></div>{report.transcript.map((item,i)=><div className="transcript-item" key={i}><div className="transcript-q"><span>0{i+1}</span><b>{item.question}</b><strong>{item.score}/10</strong></div><div className="transcript-answer"><small>YOUR ANSWER</small><p>{item.answer}</p><small>FEEDBACK</small><p>{item.feedback}</p></div></div>)}</div>
        <div className="report-actions"><p><ShieldCheck size={14}/> Scores are indicative practice feedback, not a hiring decision.</p><button className="primary-button" onClick={reset}>Start a new interview <ArrowRight size={17}/></button></div>
      </section>}
    </main>
    <footer className="footer"><span>© 2026 ROLEWISE AI</span><span>Built for better technical interviews <span className="footer-star">✳</span></span></footer>
  </div>;
}

export default App;
