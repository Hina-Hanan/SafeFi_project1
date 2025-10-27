import os
from pydantic import BaseModel
from dotenv import load_dotenv


class Settings(BaseModel):
    environment: str = os.getenv("ENVIRONMENT", "local")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://defi_user:usersafety@localhost:5432/defi_risk_assessment",
    )  # Note: This default should match your actual database name
    mlflow_tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    
    # LLM Configuration (Ollama)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "tinyllama")  # Default to TinyLlama for efficiency
    ollama_temperature: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    ollama_embedding_model: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "all-minilm")  # Lightweight embedding model
    
    # LLM Guardrail Configuration
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))  # Conservative temperature
    llm_top_p: float = float(os.getenv("LLM_TOP_P", "0.9"))
    llm_top_k: int = int(os.getenv("LLM_TOP_K", "40"))
    llm_num_ctx: int = int(os.getenv("LLM_NUM_CTX", "4096"))
    llm_repeat_penalty: float = float(os.getenv("LLM_REPEAT_PENALTY", "1.1"))
    ollama_timeout: int = int(os.getenv("OLLAMA_TIMEOUT", "280"))  # 4.5 minutes for LLM generation
    
    # RAG Configuration
    rag_chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "500"))
    rag_chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "./data/vectorstore")
    
    # RAG Guardrail Configuration
    rag_similarity_threshold: float = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.4"))
    rag_min_context_docs: int = int(os.getenv("RAG_MIN_CONTEXT_DOCS", "2"))
    
    # Email Alert Configuration
    email_alerts_enabled: bool = os.getenv("EMAIL_ALERTS_ENABLED", "false").lower() == "true"
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    alert_sender_email: str = os.getenv("ALERT_SENDER_EMAIL", "")
    alert_sender_password: str = os.getenv("ALERT_SENDER_PASSWORD", "")


load_dotenv()
settings = Settings()



