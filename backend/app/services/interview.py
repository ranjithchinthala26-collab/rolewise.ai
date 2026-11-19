import json
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
from app.core.config import settings
from app.services.rag import rag

ROLE_TOPICS = {
    "Backend Engineer": ["API design", "database transactions", "authentication", "caching", "error handling"],
    "AI/ML Engineer": ["supervised learning", "model evaluation", "feature engineering", "embeddings", "retrieval-augmented generation"],
    "Python Developer": ["Python data structures", "object-oriented programming", "exception handling", "API development", "testing"],
    "Full Stack Developer": ["frontend state", "REST APIs", "database design", "authentication", "deployment"],
}

class InterviewEngine:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key and OpenAI else None

    def make_query(self, role: str, skills: list[str], resume: str, previous_answers: list[str], index: int) -> str:
        topics = ROLE_TOPICS.get(role, ROLE_TOPICS["Backend Engineer"])
        skill_focus = ", ".join(skills[:8]) or "foundational concepts"
        answer_focus = previous_answers[-1][:250] if previous_answers else "No previous answer"
        topic = topics[index % len(topics)]
        return f"Role: {role}. Candidate skills: {skill_focus}. Evaluate {topic}. Resume evidence: {resume[:700]}. Previous answer: {answer_focus}. Explain concepts, tradeoffs and practical implementation."

    def generate_question(self, role: str, skills: list[str], resume: str, previous_answers: list[str], index: int) -> tuple[str, str, str, list[dict]]:
        query = self.make_query(role, skills, resume, previous_answers, index)
        retrieved = rag.retrieve(query, role, 4)
        topic = ROLE_TOPICS.get(role, ROLE_TOPICS["Backend Engineer"])[index % len(ROLE_TOPICS.get(role, ROLE_TOPICS["Backend Engineer"]))]
        context = "\n\n".join(x["text"] for x in retrieved) or "No matching knowledge-base chunks were retrieved. Use the role and resume context to frame a foundational question."
        difficulty = "Intermediate" if index < 2 else "Advanced"
        question = None
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=settings.openai_model, temperature=0.65,
                    messages=[
                        {"role": "system", "content": "You are a fair technical interviewer. Create exactly one concise, specific interview question. Ground it in the supplied retrieved context and candidate resume. Avoid generic questions. Do not invent resume experience. Return only the question."},
                        {"role": "user", "content": f"Role: {role}\nCandidate skills: {skills}\nResume excerpt: {resume[:1200]}\nTopic: {topic}\nDifficulty: {difficulty}\nRetrieved knowledge:\n{context}\nPrevious answers: {previous_answers[-2:]}"}
                    ]
                )
                question = response.choices[0].message.content.strip()
            except Exception:
                question = None
        if not question:
            question = self._fallback_question(role, skills, topic, context, index)
        return question, topic, difficulty, retrieved

    @staticmethod
    def _fallback_question(role, skills, topic, context, index):
        skill = next((s for s in skills if s.lower() in context.lower()), skills[0] if skills else role)
        evidence = "" if context.startswith("No matching knowledge-base chunks") else next((part.strip() for part in context.split(".") if len(part.strip()) > 55), "")
        if evidence:
            return (f"Your resume mentions {skill}. The retrieved reference explains that {evidence[:240]}. "
                    f"Explain this idea in your own words, then describe how you would apply it in a {role.lower()} task. "
                    "What trade-offs or failure cases would you consider?")
        prompts = [
            f"Your resume mentions {skill}. In the context of {topic}, explain the underlying concept and walk through how you would apply it in a real {role.lower()} task.",
            f"For {topic}, describe a design you would choose for a {role.lower()} system. What trade-offs would you consider, and why?",
            f"Suppose a production issue occurs involving {topic}. How would you investigate it, identify the root cause, and validate your fix?"
        ]
        return prompts[index % len(prompts)]

    def evaluate_answer(self, question: str, answer: str, context: str) -> tuple[float, str]:
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=settings.openai_model, temperature=0.2,
                    messages=[
                        {"role": "system", "content": "Assess a technical interview answer fairly. Return JSON with score (0-10), feedback (2-3 concise sentences), and do not reward unsupported claims. Evaluate correctness, clarity, practical reasoning, and use of relevant concepts."},
                        {"role": "user", "content": f"Question: {question}\nAnswer: {answer}\nReference context: {context[:2500]}"}
                    ], response_format={"type": "json_object"}
                )
                data = json.loads(response.choices[0].message.content)
                return max(0, min(10, float(data.get("score", 0)))), str(data.get("feedback", "Answer reviewed."))
            except Exception:
                pass
        words = len(answer.split())
        concept_hits = sum(1 for token in set(context.lower().split()) if len(token) > 5 and token in answer.lower())
        score = min(8.5, 2.0 + min(words / 45, 3.0) + min(concept_hits * 0.35, 3.5))
        if words < 12: score = min(score, 3.0)
        feedback = ("Your answer has a clear starting point. Add a concrete example, explain the reasoning behind your choice, and mention relevant trade-offs." if words < 45 else "You provided a useful explanation. Strengthen it by making the connection to the underlying concepts explicit and adding a practical example or validation step.")
        return round(score, 1), feedback

engine = InterviewEngine()
