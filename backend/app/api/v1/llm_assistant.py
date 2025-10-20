"""
LLM Assistant API Endpoints

FastAPI endpoints for RAG-powered LLM assistant using Ollama.
Supports both streaming and non-streaming responses.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.rag.llm_service import get_llm_service, RAGLLMService
from app.services.rag.vector_store import get_vector_store_manager, initialize_vector_store

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class QueryRequest(BaseModel):
    """Request for LLM query."""
    query: str = Field(..., description="User's question", min_length=1, max_length=2000)
    top_k: Optional[int] = Field(default=5, description="Number of context documents to retrieve", ge=1, le=20)
    temperature: Optional[float] = Field(default=None, description="Sampling temperature", ge=0.0, le=1.0)


class QueryResponse(BaseModel):
    """Response from LLM query."""
    answer: str = Field(..., description="Generated answer")
    context_used: int = Field(..., description="Number of context documents used")
    model: str = Field(..., description="Model used")


class VectorStoreStatus(BaseModel):
    """Vector store status."""
    initialized: bool
    document_count: Optional[int] = None
    message: str


class HealthResponse(BaseModel):
    """Health check response."""
    ollama_available: bool
    vector_store_initialized: bool
    model: str
    message: str


@router.get("/health", response_model=HealthResponse)
async def health_check(
    llm_service: RAGLLMService = Depends(get_llm_service),
) -> HealthResponse:
    """
    Check LLM assistant health.
    
    Returns:
        Health status including Ollama and vector store
    """
    try:
        # Check Ollama connection
        try:
            import httpx
            response = httpx.get(llm_service.base_url, timeout=5.0)
            ollama_available = response.status_code == 200
        except Exception:
            ollama_available = False
        
        # Check vector store
        vector_store_initialized = llm_service.vector_store_manager.vectorstore is not None
        
        if ollama_available and vector_store_initialized:
            message = "LLM Assistant is ready"
        elif not ollama_available:
            message = "Ollama service is not available. Run: ollama serve"
        else:
            message = "Vector store not initialized. Call /initialize endpoint"
        
        return HealthResponse(
            ollama_available=ollama_available,
            vector_store_initialized=vector_store_initialized,
            model=llm_service.model,
            message=message,
        )
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            ollama_available=False,
            vector_store_initialized=False,
            model="unknown",
            message=f"Error: {str(e)}",
        )


@router.post("/initialize", response_model=VectorStoreStatus)
async def initialize_vector_store_endpoint(
    db: Session = Depends(get_db),
    llm_service: RAGLLMService = Depends(get_llm_service),
) -> VectorStoreStatus:
    """
    Initialize vector store with database documents.
    
    This endpoint loads all protocols, risk scores, and system information
    from the database and creates embeddings for semantic search.
    
    Returns:
        Vector store status
    """
    try:
        logger.info("Initializing vector store from API endpoint")
        manager = initialize_vector_store(db)
        
        document_count = None
        if manager.vectorstore:
            try:
                # Try to get collection count (ChromaDB)
                if hasattr(manager.vectorstore, '_collection'):
                    document_count = manager.vectorstore._collection.count()
            except Exception:
                pass
        
        return VectorStoreStatus(
            initialized=manager.vectorstore is not None,
            document_count=document_count,
            message="Vector store initialized successfully" if manager.vectorstore else "Failed to initialize",
        )
    
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize vector store: {str(e)}",
        ) from e


@router.post("/refresh", response_model=VectorStoreStatus)
async def refresh_vector_store_endpoint(
    db: Session = Depends(get_db),
    llm_service: RAGLLMService = Depends(get_llm_service),
) -> VectorStoreStatus:
    """
    Refresh vector store with latest database data.
    
    Call this endpoint after adding new protocols or updating risk scores
    to ensure the LLM has access to the latest information.
    
    Returns:
        Updated vector store status
    """
    try:
        logger.info("Refreshing vector store from API endpoint")
        llm_service.refresh_vector_store(db)
        
        manager = get_vector_store_manager()
        document_count = None
        if manager.vectorstore:
            try:
                if hasattr(manager.vectorstore, '_collection'):
                    document_count = manager.vectorstore._collection.count()
            except Exception:
                pass
        
        return VectorStoreStatus(
            initialized=True,
            document_count=document_count,
            message="Vector store refreshed successfully",
        )
    
    except Exception as e:
        logger.error(f"Failed to refresh vector store: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh vector store: {str(e)}",
        ) from e


@router.post("/query", response_model=QueryResponse)
async def query_llm(
    request: QueryRequest,
    db: Session = Depends(get_db),
    llm_service: RAGLLMService = Depends(get_llm_service),
) -> QueryResponse:
    """
    Query LLM assistant with RAG (non-streaming).
    
    The assistant will:
    1. Search the vector store for relevant context
    2. Retrieve matching documents from database
    3. Generate a response using the LLM with context
    
    Args:
        request: Query request with question and parameters
        db: Database session
        llm_service: LLM service instance
    
    Returns:
        Generated answer with metadata
    
    Example:
        ```json
        {
            "query": "What are the high-risk protocols?",
            "top_k": 5
        }
        ```
    """
    try:
        # Ensure vector store is initialized
        llm_service.ensure_vector_store(db)
        
        # Retrieve relevant context
        context_docs = llm_service.retrieve_context(request.query, k=request.top_k)
        
        # Generate response
        if request.temperature is not None:
            llm_service.llm.temperature = request.temperature
        
        answer = llm_service.generate_response(
            query=request.query,
            context_documents=context_docs,
            db=db,
        )
        
        return QueryResponse(
            answer=answer,
            context_used=len(context_docs),
            model=llm_service.model,
        )
    
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}",
        ) from e


@router.post("/query/stream")
async def query_llm_stream(
    request: QueryRequest,
    db: Session = Depends(get_db),
    llm_service: RAGLLMService = Depends(get_llm_service),
) -> StreamingResponse:
    """
    Query LLM assistant with streaming response.
    
    Returns Server-Sent Events (SSE) stream with response tokens.
    
    Args:
        request: Query request
        db: Database session
        llm_service: LLM service instance
    
    Returns:
        Streaming response with text/event-stream content type
    
    Example:
        ```bash
        curl -X POST http://localhost:8000/api/v1/llm/query/stream \\
          -H "Content-Type: application/json" \\
          -d '{"query": "What protocols are monitored?"}'
        ```
    """
    
    async def generate_stream():
        """Generate SSE stream."""
        try:
            # Ensure vector store is initialized
            llm_service.ensure_vector_store(db)
            
            # Retrieve relevant context
            context_docs = llm_service.retrieve_context(request.query, k=request.top_k)
            
            # Update temperature if specified
            if request.temperature is not None:
                llm_service.llm.temperature = request.temperature
            
            # Stream response
            async for token in llm_service.generate_response_stream(
                query=request.query,
                context_documents=context_docs,
                db=db,
            ):
                yield f"data: {token}\n\n"
            
            # Send completion marker
            yield "data: [DONE]\n\n"
        
        except Exception as e:
            logger.error(f"Streaming query failed: {e}")
            yield f"data: [ERROR] {str(e)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/context/{query}")
async def get_context(
    query: str,
    top_k: int = 5,
    llm_service: RAGLLMService = Depends(get_llm_service),
    db: Session = Depends(get_db),
) -> dict:
    """
    Retrieve relevant context documents without generating response.
    
    Useful for debugging and understanding what context the LLM will use.
    
    Args:
        query: Search query
        top_k: Number of documents to retrieve
        llm_service: LLM service instance
        db: Database session
    
    Returns:
        Dictionary with retrieved documents and metadata
    """
    try:
        llm_service.ensure_vector_store(db)
        
        documents = llm_service.retrieve_context(query, k=top_k)
        
        return {
            "query": query,
            "documents_found": len(documents),
            "documents": [
                {
                    "content": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                    "metadata": doc.metadata,
                }
                for doc in documents
            ],
        }
    
    except Exception as e:
        logger.error(f"Context retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Context retrieval failed: {str(e)}",
        ) from e


