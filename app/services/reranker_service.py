from sentence_transformers import CrossEncoder


class RerankerService:
    def __init__(self):
        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def rerank(self, question: str, chunks: list[str], top_k: int = 5) -> list[str]:
        scores = self.model.predict([(question, chunk) for chunk in chunks])
        ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
        return [text for text, score in ranked[:top_k]]