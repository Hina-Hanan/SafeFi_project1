"""
LLM Service with RAG (Retrieval-Augmented Generation)

Integrates Ollama LLM with vector store for context-aware responses.
Uses LangChain for orchestration.
"""

import logging
from typing import List, AsyncGenerator, Optional

from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_core.documents import Document
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.rag.vector_store import get_vector_store_manager, initialize_vector_store

logger = logging.getLogger(__name__)


# System prompt template for RAG
RAG_PROMPT_TEMPLATE = """You are an AI assistant for a DeFi (Decentralized Finance) Risk Assessment platform. 
You help users understand protocol risks, metrics, and market data.

Use the following context from our database to answer the question. If you don't know the answer based on the context, say so - don't make up information.

Context:
{context}

Question: {question}

Answer: Provide a clear, concise answer based on the context above. Include specific numbers and data points when available. If asked about protocols, mention their risk levels and key metrics."""


class RAGLLMService:
    """
    LLM service with Retrieval-Augmented Generation capabilities.
    
    Combines vector search with LLM generation for accurate, context-aware responses.
    """
    
    def __init__(
        self,
        model: str = settings.ollama_model,
        base_url: str = settings.ollama_base_url,
        temperature: float = settings.ollama_temperature,
    ):
        """
        Initialize RAG LLM service.
        
        Args:
            model: Ollama model name
            base_url: Ollama API base URL
            temperature: Sampling temperature
        """
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        
        # Initialize Ollama LLM
        logger.info(f"Initializing Ollama LLM: {model} at {base_url}")
        self.llm = Ollama(
            model=self.model,
            base_url=self.base_url,
            temperature=self.temperature,
        )
        
        # Vector store manager
        self.vector_store_manager = get_vector_store_manager()
        
        # Prompt template
        self.prompt_template = PromptTemplate(
            template=RAG_PROMPT_TEMPLATE,
            input_variables=["context", "question"],
        )
    
    def ensure_vector_store(self, db: Session) -> None:
        """
        Ensure vector store is initialized.
        
        Args:
            db: Database session
        """
        if self.vector_store_manager.vectorstore is None:
            logger.info("Vector store not initialized, creating...")
            try:
                initialize_vector_store(db)
                logger.info("Vector store initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize vector store: {e}")
                raise
    
    def retrieve_context(self, query: str, k: int = settings.rag_top_k) -> List[Document]:
        """
        Retrieve relevant documents for query.
        
        Args:
            query: User query
            k: Number of documents to retrieve
        
        Returns:
            List of relevant documents
        """
        if self.vector_store_manager.vectorstore is None:
            logger.warning("Vector store not initialized")
            return []
        
        try:
            documents = self.vector_store_manager.similarity_search(query, k=k)
            logger.info(f"Retrieved {len(documents)} relevant documents")
            return documents
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return []
    
    def generate_response(
        self,
        query: str,
        context_documents: Optional[List[Document]] = None,
        db: Optional[Session] = None,
    ) -> str:
        """
        Generate response using RAG.
        
        Args:
            query: User question
            context_documents: Pre-retrieved documents (optional)
            db: Database session for on-demand retrieval
        
        Returns:
            Generated response
        """
        try:
            # Ensure vector store is initialized
            if db:
                self.ensure_vector_store(db)
            
            # Retrieve context if not provided
            if context_documents is None:
                context_documents = self.retrieve_context(query)
            
            # Build context string
            if context_documents:
                context = "\n\n".join([doc.page_content for doc in context_documents])
            else:
                context = "No specific context available from database."
            
            # Format prompt
            prompt = self.prompt_template.format(context=context, question=query)
            
            # Generate response
            logger.info(f"Generating response for query: {query[:100]}...")
            response = self.llm.invoke(prompt)
            
            return response
        
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    async def generate_response_stream(
        self,
        query: str,
        context_documents: Optional[List[Document]] = None,
        db: Optional[Session] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response using RAG.
        
        Args:
            query: User question
            context_documents: Pre-retrieved documents (optional)
            db: Database session for on-demand retrieval
        
        Yields:
            Response tokens
        """
        try:
            # Ensure vector store is initialized
            if db:
                self.ensure_vector_store(db)
            
            # Retrieve context if not provided
            if context_documents is None:
                context_documents = self.retrieve_context(query)
            
            # Build context string
            if context_documents:
                context = "\n\n".join([doc.page_content for doc in context_documents])
            else:
                context = "No specific context available from database."
            
            # Format prompt
            prompt = self.prompt_template.format(context=context, question=query)
            
            # Stream response
            logger.info(f"Streaming response for query: {query[:100]}...")
            
            # LangChain's Ollama doesn't have built-in async streaming,
            # so we use the underlying httpx client
            import httpx
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {"temperature": self.temperature},
                    },
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                import json
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
        
        except Exception as e:
            logger.error(f"Failed to stream response: {e}")
            yield f"Error: {str(e)}"
    
    def refresh_vector_store(self, db: Session) -> None:
        """
        Refresh vector store with latest database data.
        
        Args:
            db: Database session
        """
        logger.info("Refreshing vector store")
        self.vector_store_manager.refresh_from_database(db)
        logger.info("Vector store refreshed")


# Global LLM service instance
_llm_service: Optional[RAGLLMService] = None


def get_llm_service() -> RAGLLMService:
    """
    Get or create global LLM service instance.
    
    Returns:
        RAGLLMService instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = RAGLLMService()
    return _llm_service


