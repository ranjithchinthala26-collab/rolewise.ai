"""Index the documents placed in backend/data/knowledge_base."""
from app.services.rag import rag

if __name__ == "__main__":
    count = rag.ingest_directory()
    print(f"Indexed {count} chunks. Total collection size: {rag.collection.count()}")
