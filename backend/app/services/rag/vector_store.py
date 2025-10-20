"""
Vector Store Management for RAG

Handles document embeddings and semantic search using ChromaDB and FAISS.
"""

import logging
import os
from typing import List, Optional

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import Chroma, FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.rag.document_loaders import get_document_loader

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manages vector store for document embeddings and retrieval.
    
    Supports both ChromaDB (persistent) and FAISS (in-memory) vector stores.
    """
    
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        persist_directory: Optional[str] = None,
        use_faiss: bool = False,
    ):
        """
        Initialize vector store manager.
        
        Args:
            embedding_model: HuggingFace model for embeddings
            persist_directory: Directory to persist vector store
            use_faiss: Use FAISS instead of ChromaDB (faster but in-memory)
        """
        self.embedding_model_name = embedding_model
        self.persist_directory = persist_directory or settings.vector_store_path
        self.use_faiss = use_faiss
        
        # Initialize embeddings
        logger.info(f"Loading embedding model: {self.embedding_model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model_name,
            model_kwargs={"device": "cpu"},  # Use GPU if available
            encode_kwargs={"normalize_embeddings": True},
        )
        
        self.vectorstore: Optional[Chroma | FAISS] = None
    
    def create_vectorstore(self, documents: List[Document]) -> None:
        """
        Create vector store from documents.
        
        Args:
            documents: List of documents to embed
        """
        if not documents:
            logger.warning("No documents provided to create vector store")
            return
        
        logger.info(f"Creating vector store from {len(documents)} documents")
        
        try:
            if self.use_faiss:
                # Use FAISS for fast in-memory search
                self.vectorstore = FAISS.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                )
                logger.info("FAISS vector store created successfully")
            else:
                # Use ChromaDB for persistent storage
                os.makedirs(self.persist_directory, exist_ok=True)
                self.vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory,
                )
                logger.info(f"ChromaDB vector store created at {self.persist_directory}")
        
        except Exception as e:
            logger.error(f"Failed to create vector store: {e}")
            raise
    
    def load_vectorstore(self) -> bool:
        """
        Load existing vector store from disk (ChromaDB only).
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if self.use_faiss:
            logger.warning("FAISS does not support loading from disk")
            return False
        
        if not os.path.exists(self.persist_directory):
            logger.info(f"No existing vector store found at {self.persist_directory}")
            return False
        
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
            )
            logger.info("Vector store loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            return False
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to existing vector store.
        
        Args:
            documents: Documents to add
        """
        if not self.vectorstore:
            logger.error("Vector store not initialized")
            raise ValueError("Vector store must be created or loaded first")
        
        if not documents:
            logger.warning("No documents to add")
            return
        
        try:
            self.vectorstore.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[dict] = None,
    ) -> List[Document]:
        """
        Perform similarity search on vector store.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Metadata filters (e.g., {"type": "protocol"})
        
        Returns:
            List of most similar documents
        """
        if not self.vectorstore:
            logger.error("Vector store not initialized")
            return []
        
        try:
            results = self.vectorstore.similarity_search(
                query=query,
                k=k,
                filter=filter_dict,
            )
            logger.info(f"Found {len(results)} similar documents for query: {query[:50]}...")
            return results
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[dict] = None,
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search with relevance scores.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Metadata filters
        
        Returns:
            List of (document, score) tuples
        """
        if not self.vectorstore:
            logger.error("Vector store not initialized")
            return []
        
        try:
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter_dict,
            )
            logger.info(f"Found {len(results)} results with scores")
            return results
        except Exception as e:
            logger.error(f"Similarity search with score failed: {e}")
            return []
    
    def delete_vectorstore(self) -> None:
        """Delete vector store (ChromaDB only)."""
        if self.use_faiss:
            self.vectorstore = None
            logger.info("FAISS vector store cleared from memory")
            return
        
        try:
            if os.path.exists(self.persist_directory):
                import shutil
                shutil.rmtree(self.persist_directory)
                logger.info(f"Deleted vector store at {self.persist_directory}")
            self.vectorstore = None
        except Exception as e:
            logger.error(f"Failed to delete vector store: {e}")
    
    def refresh_from_database(self, db: Session) -> None:
        """
        Refresh vector store with latest database documents.
        
        Args:
            db: Database session
        """
        logger.info("Refreshing vector store from database")
        
        # Load documents from database
        loader = get_document_loader(db)
        documents = loader.load_all_documents()
        
        if not documents:
            logger.warning("No documents loaded from database")
            return
        
        # Recreate vector store
        if not self.use_faiss:
            self.delete_vectorstore()
        
        self.create_vectorstore(documents)
        logger.info("Vector store refreshed successfully")


# Global vector store instance
_vector_store_manager: Optional[VectorStoreManager] = None


def get_vector_store_manager() -> VectorStoreManager:
    """
    Get or create global vector store manager.
    
    Returns:
        VectorStoreManager instance
    """
    global _vector_store_manager
    if _vector_store_manager is None:
        _vector_store_manager = VectorStoreManager(
            use_faiss=True,  # Use FAISS for faster in-memory search
        )
    return _vector_store_manager


def initialize_vector_store(db: Session) -> VectorStoreManager:
    """
    Initialize vector store with database documents.
    
    Args:
        db: Database session
    
    Returns:
        Initialized VectorStoreManager
    """
    manager = get_vector_store_manager()
    
    # Try to load existing store
    if not manager.use_faiss:
        loaded = manager.load_vectorstore()
        if loaded:
            logger.info("Using existing vector store")
            return manager
    
    # Create new store from database
    logger.info("Creating new vector store from database")
    loader = get_document_loader(db)
    documents = loader.load_all_documents()
    
    if documents:
        manager.create_vectorstore(documents)
    else:
        logger.warning("No documents found in database")
    
    return manager


