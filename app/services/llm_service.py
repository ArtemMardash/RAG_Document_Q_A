from groq import Groq
from app.core.config import GROQ_API_KEY, GROQ_MODEL


class LLMService:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL

    def answer(self, question: str, context_chunks: list[str]) -> str:
        prompt = self._build_prompt(question, context_chunks)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def _build_prompt(self, question: str, chunks: list[str]) -> str:
        context = "\n\n---\n\n".join(chunks)
        return f"""You are a helpful assistant. Answer the question using ONLY the context provided below. 
If the answer is not in the context, say "I could not find the answer in the provided document."

Context:
{context}

Question: {question}

Answer:"""