from app.services.rag import KnowledgeRetriever

def test_chunking_preserves_text():
    source = ("A sentence about vector retrieval and semantic embeddings. " * 60)
    chunks = KnowledgeRetriever._chunk(source, size=350, overlap=50)
    assert len(chunks) > 1
    assert all(len(chunk) > 80 for chunk in chunks)
