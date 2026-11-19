from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "RoleWise AI"
    database_url: str = "sqlite:///./rolewise.db"
    chroma_path: str = "./data/chroma"
    knowledge_base_path: str = "./data/knowledge_base"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    frontend_origin: str = "http://localhost:5173"
    max_upload_mb: int = 10
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
