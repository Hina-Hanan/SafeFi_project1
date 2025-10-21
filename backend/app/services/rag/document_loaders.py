"""
Document Loaders for RAG System

Converts database records and system data into documents for vector embeddings.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from langchain_core.documents import Document
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.database.models import Protocol, ProtocolMetric, RiskScore, Alert

logger = logging.getLogger(__name__)


class DatabaseDocumentLoader:
    """
    Loads data from database and converts to LangChain Documents.
    
    Documents are used for vector embeddings and retrieval in RAG pipeline.
    """
    
    def __init__(self, db: Session):
        """
        Initialize document loader.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def load_protocol_documents(self, limit: int = 100) -> List[Document]:
        """
        Load protocol documents with latest metrics and risk scores.
        
        Args:
            limit: Maximum number of protocols to load
        
        Returns:
            List of Document objects with protocol information
        """
        documents = []
        
        try:
            stmt = select(Protocol).where(Protocol.is_active == True).limit(limit)
            protocols = self.db.scalars(stmt).all()
            
            for protocol in protocols:
                # Get latest metric
                latest_metric_stmt = (
                    select(ProtocolMetric)
                    .where(ProtocolMetric.protocol_id == protocol.id)
                    .order_by(desc(ProtocolMetric.timestamp))
                    .limit(1)
                )
                latest_metric = self.db.scalar(latest_metric_stmt)
                
                # Get latest risk score
                latest_risk_stmt = (
                    select(RiskScore)
                    .where(RiskScore.protocol_id == protocol.id)
                    .order_by(desc(RiskScore.timestamp))
                    .limit(1)
                )
                latest_risk = self.db.scalar(latest_risk_stmt)
                
                # Build document content
                content = self._build_protocol_content(protocol, latest_metric, latest_risk)
                
                # Create metadata
                metadata = {
                    "source": "database",
                    "type": "protocol",
                    "protocol_id": protocol.id,
                    "protocol_name": protocol.name,
                    "category": protocol.category,
                    "chain": protocol.chain,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                
                if latest_risk:
                    metadata["risk_level"] = latest_risk.risk_level
                    metadata["risk_score"] = latest_risk.risk_score
                
                documents.append(Document(page_content=content, metadata=metadata))
            
            logger.info(f"Loaded {len(documents)} protocol documents")
            return documents
        
        except Exception as e:
            logger.error(f"Failed to load protocol documents: {e}")
            return []
    
    def _build_protocol_content(
        self,
        protocol: Protocol,
        metric: ProtocolMetric | None,
        risk: RiskScore | None
    ) -> str:
        """Build text content for protocol document."""
        lines = [
            f"Protocol: {protocol.name}",
            f"Symbol: {protocol.symbol or 'N/A'}",
            f"Category: {protocol.category}",
            f"Blockchain: {protocol.chain}",
        ]
        
        if protocol.contract_address:
            lines.append(f"Contract Address: {protocol.contract_address}")
        
        if metric:
            lines.append(f"\nLatest Metrics (as of {metric.timestamp.strftime('%Y-%m-%d %H:%M')}):")
            if metric.tvl:
                lines.append(f"- Total Value Locked (TVL): ${float(metric.tvl):,.2f}")
            if metric.volume_24h:
                lines.append(f"- 24h Volume: ${float(metric.volume_24h):,.2f}")
            if metric.price:
                lines.append(f"- Price: ${float(metric.price):.8f}")
            if metric.market_cap:
                lines.append(f"- Market Cap: ${float(metric.market_cap):,.2f}")
            if metric.price_change_24h is not None:
                lines.append(f"- 24h Price Change: {metric.price_change_24h:.2f}%")
        
        if risk:
            lines.append(f"\nRisk Assessment (as of {risk.timestamp.strftime('%Y-%m-%d %H:%M')}):")
            lines.append(f"- Risk Level: {risk.risk_level.upper()}")
            lines.append(f"- Risk Score: {risk.risk_score:.2f}")
            if risk.volatility_score:
                lines.append(f"- Volatility Score: {risk.volatility_score:.2f}")
            if risk.liquidity_score:
                lines.append(f"- Liquidity Score: {risk.liquidity_score:.2f}")
            # Model version stored in metadata only, not shown to LLM
        
        return "\n".join(lines)
    
    def load_risk_summary_documents(self) -> List[Document]:
        """
        Load summary documents for risk scores by category and level.
        
        Returns:
            List of Document objects with risk summaries
        """
        documents = []
        
        try:
            # Get latest risk scores for each protocol
            subquery = (
                select(
                    RiskScore.protocol_id,
                    RiskScore.risk_level,
                    RiskScore.risk_score,
                )
                .distinct(RiskScore.protocol_id)
                .order_by(RiskScore.protocol_id, desc(RiskScore.timestamp))
                .subquery()
            )
            
            results = self.db.execute(select(subquery)).all()
            
            # Group by risk level
            risk_groups: Dict[str, List[Dict]] = {"high": [], "medium": [], "low": []}
            
            for protocol_id, risk_level, risk_score in results:
                protocol = self.db.get(Protocol, protocol_id)
                if protocol:
                    risk_groups[risk_level].append({
                        "name": protocol.name,
                        "category": protocol.category,
                        "score": risk_score,
                    })
            
            # Create summary document
            content_lines = ["DeFi Risk Assessment Summary\n"]
            
            for level in ["high", "medium", "low"]:
                protocols = risk_groups[level]
                content_lines.append(f"\n{level.upper()} RISK Protocols ({len(protocols)} total):")
                
                for p in protocols[:10]:  # Top 10
                    content_lines.append(
                        f"- {p['name']} ({p['category']}): Risk Score {p['score']:.2f}"
                    )
            
            documents.append(
                Document(
                    page_content="\n".join(content_lines),
                    metadata={
                        "source": "database",
                        "type": "risk_summary",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            )
            
            logger.info("Loaded risk summary document")
            return documents
        
        except Exception as e:
            logger.error(f"Failed to load risk summary documents: {e}")
            return []
    
    def load_system_info_documents(self) -> List[Document]:
        """
        Load system information documents.
        
        Returns:
            List of Document objects with system info
        """
        documents = []
        
        try:
            # System overview
            total_protocols = self.db.scalar(select(Protocol).count()) or 0
            total_active = self.db.scalar(
                select(Protocol).where(Protocol.is_active == True).count()
            ) or 0
            total_metrics = self.db.scalar(select(ProtocolMetric).count()) or 0
            total_risks = self.db.scalar(select(RiskScore).count()) or 0
            
            content = f"""DeFi Risk Assessment Platform - System Information

Overview:
The DeFi Risk Assessment Platform monitors decentralized finance protocols across multiple blockchains,
providing real-time risk analysis using machine learning models and on-chain data.

Current Statistics:
- Total Protocols Tracked: {total_protocols}
- Active Protocols: {total_active}
- Metrics Records: {total_metrics}
- Risk Assessments: {total_risks}

Features:
- Real-time protocol monitoring
- ML-powered risk scoring using Random Forest, XGBoost, and Logistic Regression models
- Anomaly detection for unusual protocol behavior
- Alert system for high-risk events
- Historical trend analysis
- Multi-chain support (Ethereum, BSC, Polygon, etc.)

Risk Scoring Methodology:
Risk scores are calculated based on multiple factors including:
- Total Value Locked (TVL) volatility
- Trading volume patterns
- Price stability
- Liquidity depth
- Smart contract security metrics
- Historical performance

Risk Levels:
- LOW (0.0-0.33): Stable protocols with low volatility and high liquidity
- MEDIUM (0.33-0.66): Moderate risk protocols with some volatility
- HIGH (0.66-1.0): High-risk protocols with significant volatility or low liquidity

Data Sources:
- CoinGecko API for price and market data
- DeFiLlama for TVL and protocol statistics
- On-chain data for transaction volumes
"""
            
            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": "system",
                        "type": "system_info",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            )
            
            logger.info("Loaded system info document")
            return documents
        
        except Exception as e:
            logger.error(f"Failed to load system info documents: {e}")
            return []
    
    def load_all_documents(self) -> List[Document]:
        """
        Load all available documents from database.
        
        Returns:
            List of all Document objects
        """
        all_docs = []
        all_docs.extend(self.load_protocol_documents())
        all_docs.extend(self.load_risk_summary_documents())
        all_docs.extend(self.load_system_info_documents())
        
        logger.info(f"Loaded {len(all_docs)} total documents")
        return all_docs


def get_document_loader(db: Session) -> DatabaseDocumentLoader:
    """
    Get document loader instance.
    
    Args:
        db: Database session
    
    Returns:
        DatabaseDocumentLoader instance
    """
    return DatabaseDocumentLoader(db)


