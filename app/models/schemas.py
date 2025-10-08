"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role in chat."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class EnrichmentType(str, Enum):
    """Types of enrichment suggestions."""
    DOCUMENT = "document"
    EXTERNAL_SOURCE = "external_source"
    CLARIFICATION = "clarification"
    RELATED_TOPIC = "related_topic"


class SourceReference(BaseModel):
    """Reference to a source document."""
    document_id: str
    document_name: str
    chunk_id: str
    content: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EnrichmentSuggestion(BaseModel):
    """Suggestion for enriching the knowledge base."""
    type: EnrichmentType
    suggestion: str
    priority: str = Field(..., description="high, medium, or low")
    reasoning: str
    auto_enrichment_available: bool = False
    external_source_url: Optional[str] = None


class SearchRequest(BaseModel):
    """Request model for search queries."""
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: Optional[int] = Field(default=5, ge=1, le=20)
    enable_auto_enrichment: bool = Field(default=False)


class SearchResponse(BaseModel):
    """Response model for search queries with structured output."""
    query: str
    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    is_complete: bool
    sources: List[SourceReference]
    missing_info: List[str] = Field(default_factory=list)
    enrichment_suggestions: List[EnrichmentSuggestion] = Field(default_factory=list)
    auto_enrichment_applied: bool = False
    auto_enrichment_sources: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    document_id: str
    filename: str
    file_size: int
    file_type: str
    chunks_created: int
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    message: str = "Document uploaded and processed successfully"


class DocumentInfo(BaseModel):
    """Information about a stored document."""
    document_id: str
    filename: str
    file_size: int
    file_type: str
    upload_timestamp: datetime
    chunks_count: int


class DocumentListResponse(BaseModel):
    """Response model for listing documents."""
    documents: List[DocumentInfo]
    total_count: int


class RatingRequest(BaseModel):
    """Request model for rating an answer."""
    query: str
    answer: str
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None


class RatingResponse(BaseModel):
    """Response model for rating submission."""
    message: str = "Rating recorded successfully"
    rating_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str = "1.0.0"
    vector_store_status: str
    documents_count: int


# ============================================================================
# CHAT & SESSION MODELS (V2.0)
# ============================================================================

class ChatMessage(BaseModel):
    """A single chat message."""
    role: MessageRole
    content: str
    timestamp: datetime
    sources: List[SourceReference] = Field(default_factory=list)
    confidence: Optional[float] = None
    web_search_used: bool = False


class SessionResponse(BaseModel):
    """Response model for session information."""
    session_id: str
    name: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class ChatRequest(BaseModel):
    """Request model for chat interaction."""
    session_id: str
    message: str = Field(..., min_length=1, max_length=2000)
    enable_web_search: bool = Field(default=True)
    enable_auto_enrichment: bool = Field(default=True)


class ChatResponse(BaseModel):
    """Response model for chat interaction."""
    session_id: str
    message: ChatMessage


class MultiDocumentUploadResponse(BaseModel):
    """Response model for multi-document upload."""
    successful_uploads: List[DocumentUploadResponse]
    failed_uploads: List[Dict[str, str]]
    total_uploaded: int
    total_failed: int

