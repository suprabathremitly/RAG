"""API route handlers."""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List

from app.models.schemas import (
    DocumentUploadResponse,
    SearchRequest,
    SearchResponse,
    RatingRequest,
    RatingResponse,
    DocumentListResponse,
    DocumentInfo,
    HealthResponse,
    ChatRequest,
    ChatResponse,
    SessionResponse,
    MessageRole,
    MultiDocumentUploadResponse
)
from app.services.document_processor import document_processor
from app.services.vector_store import vector_store_service
from app.services.rag_pipeline import rag_pipeline
from app.services.enrichment_engine import enrichment_engine
from app.services.rating_service import rating_service
from app.services.session_manager import session_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    stats = vector_store_service.get_collection_stats()
    doc_count = vector_store_service.get_unique_documents_count()
    
    return HealthResponse(
        status="healthy",
        vector_store_status=stats['status'],
        documents_count=doc_count
    )


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document to the knowledge base.
    
    Supports: PDF, TXT, DOCX formats
    """
    try:
        # Validate file format
        if not document_processor.is_supported_format(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format. Supported formats: {document_processor.SUPPORTED_FORMATS}"
            )
        
        # Read file content
        content = await file.read()
        
        # Process document
        doc_id, chunks = await document_processor.process_upload(content, file.filename)
        
        # Add to vector store
        await vector_store_service.add_documents(chunks)
        
        return DocumentUploadResponse(
            document_id=doc_id,
            filename=file.filename,
            file_size=len(content),
            file_type=file.filename.split('.')[-1],
            chunks_created=len(chunks)
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """List all documents in the knowledge base."""
    try:
        docs = document_processor.list_documents()
        
        # Get chunk counts from vector store
        doc_infos = []
        for doc in docs:
            chunks = await vector_store_service.get_document_chunks(doc['document_id'])
            doc_infos.append(DocumentInfo(
                document_id=doc['document_id'],
                filename=doc['filename'],
                file_size=doc['file_size'],
                file_type=doc['file_type'],
                upload_timestamp=doc['upload_timestamp'],
                chunks_count=len(chunks)
            ))
        
        return DocumentListResponse(
            documents=doc_infos,
            total_count=len(doc_infos)
        )
    
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents"
        )


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the knowledge base."""
    try:
        # Delete from vector store
        vector_deleted = await vector_store_service.delete_documents(document_id)
        
        # Delete file
        file_deleted = document_processor.delete_document(document_id)
        
        if not vector_deleted and not file_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return {"message": "Document deleted successfully", "document_id": document_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search the knowledge base and get an AI-generated answer.
    
    Features:
    - Natural language search
    - Confidence scoring
    - Completeness detection
    - Enrichment suggestions
    - Optional auto-enrichment
    """
    try:
        response = await rag_pipeline.search_and_answer(
            query=request.query,
            top_k=request.top_k,
            enable_auto_enrichment=request.enable_auto_enrichment
        )
        
        # If auto-enrichment is enabled and answer is incomplete
        if request.enable_auto_enrichment and not response.is_complete:
            enrichment_result = await enrichment_engine.auto_enrich(
                query=request.query,
                missing_info=response.missing_info,
                max_sources=2
            )
            
            if enrichment_result['success']:
                # Re-run search with enriched knowledge base
                response = await rag_pipeline.search_and_answer(
                    query=request.query,
                    top_k=request.top_k,
                    enable_auto_enrichment=False
                )
                response.auto_enrichment_applied = True
                response.auto_enrichment_sources = enrichment_result['sources_added']
        
        return response
    
    except Exception as e:
        logger.error(f"Error processing search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process search query"
        )


@router.post("/rate", response_model=RatingResponse)
async def rate_answer(request: RatingRequest):
    """
    Rate the quality of an answer.
    
    Ratings help improve the system over time.
    """
    try:
        rating_id = await rating_service.save_rating(
            query=request.query,
            answer=request.answer,
            rating=request.rating,
            feedback=request.feedback
        )
        
        return RatingResponse(rating_id=rating_id)
    
    except Exception as e:
        logger.error(f"Error saving rating: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save rating"
        )


@router.get("/ratings/statistics")
async def get_rating_statistics():
    """Get statistics about answer ratings."""
    try:
        stats = rating_service.get_rating_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting rating statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rating statistics"
        )


@router.get("/enrichment/capabilities")
async def get_enrichment_capabilities():
    """Get available auto-enrichment capabilities."""
    return enrichment_engine.get_enrichment_capabilities()


# ============================================================================
# SESSION ENDPOINTS (V2.0)
# ============================================================================

@router.post("/sessions", response_model=SessionResponse)
async def create_session(name: str = None):
    """Create a new chat session."""
    try:
        session_id = session_manager.create_session(name)
        session = session_manager.get_session(session_id)

        return SessionResponse(
            session_id=session["session_id"],
            name=session["name"],
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            message_count=len(session.get("messages", []))
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )


@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions():
    """List all chat sessions."""
    try:
        return session_manager.list_sessions()
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list sessions"
        )


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific session."""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        return SessionResponse(
            session_id=session["session_id"],
            name=session["name"],
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            message_count=len(session.get("messages", []))
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session"
        )


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, limit: int = None):
    """Get messages from a session."""
    try:
        messages = session_manager.get_conversation_history(session_id, limit)
        return {"session_id": session_id, "messages": messages}
    except Exception as e:
        logger.error(f"Error getting session messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session messages"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session."""
    try:
        deleted = session_manager.delete_session(session_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        return {"message": "Session deleted successfully", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )


# ============================================================================
# CHAT ENDPOINTS (V2.0)
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat-style interaction with the knowledge base.

    Features:
    - Session-based conversation history
    - Auto-enrichment with web search
    - Context-aware responses
    """
    try:
        # Verify session exists
        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Add user message to session
        session_manager.add_message(
            session_id=request.session_id,
            role=MessageRole.USER,
            content=request.message
        )

        # Process query with RAG pipeline (includes auto-enrichment with web search)
        search_response = await rag_pipeline.search_and_answer(
            query=request.message,
            top_k=5,
            enable_auto_enrichment=request.enable_auto_enrichment
        )

        # Check if auto-enrichment was applied (web search is now part of auto-enrichment)
        web_search_used = search_response.auto_enrichment_applied

        # Add assistant message to session
        assistant_message = session_manager.add_message(
            session_id=request.session_id,
            role=MessageRole.ASSISTANT,
            content=search_response.answer,
            sources=search_response.sources,
            confidence=search_response.confidence,
            web_search_used=web_search_used
        )

        return ChatResponse(
            session_id=request.session_id,
            message=assistant_message
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )


# ============================================================================
# MULTI-DOCUMENT UPLOAD (V2.0)
# ============================================================================

@router.post("/documents/upload-multiple", response_model=MultiDocumentUploadResponse)
async def upload_multiple_documents(files: List[UploadFile] = File(...)):
    """
    Upload multiple documents at once.

    Returns success and failure lists.
    """
    successful_uploads = []
    failed_uploads = []

    for file in files:
        try:
            # Validate file format
            if not document_processor.is_supported_format(file.filename):
                failed_uploads.append({
                    "filename": file.filename,
                    "error": f"Unsupported file format. Supported: {', '.join(document_processor.SUPPORTED_FORMATS)}"
                })
                continue

            # Read file content
            content = await file.read()

            # Process document
            result = await document_processor.process_document(
                file_content=content,
                filename=file.filename
            )

            # Add to vector store
            vector_store_service.add_documents(
                documents=result['chunks'],
                document_id=result['document_id']
            )

            successful_uploads.append(DocumentUploadResponse(
                document_id=result['document_id'],
                filename=result['filename'],
                file_size=result['file_size'],
                file_type=result['file_type'],
                chunks_created=result['chunks_count']
            ))

        except Exception as e:
            logger.error(f"Error uploading {file.filename}: {e}")
            failed_uploads.append({
                "filename": file.filename,
                "error": str(e)
            })

    return MultiDocumentUploadResponse(
        successful_uploads=successful_uploads,
        failed_uploads=failed_uploads,
        total_uploaded=len(successful_uploads),
        total_failed=len(failed_uploads)
    )

