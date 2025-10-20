import os
from pydantic import BaseModel
from dotenv import load_dotenv


class Settings(BaseModel):
    environment: str = os.getenv("ENVIRONMENT", "local")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://defi_user:usersafety@localhost:5432/defi_risk_assessment",
    )
    mlflow_tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    
    # LLM Configuration (Ollama)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    ollama_temperature: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    ollama_embedding_model: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    
    # RAG Configuration
    rag_chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "500"))
    rag_chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "./data/vectorstore")


load_dotenv()
settings = Settings()



