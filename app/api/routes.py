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
    HealthResponse
)
from app.services.document_processor import document_processor
from app.services.vector_store import vector_store_service
from app.services.rag_pipeline import rag_pipeline
from app.services.enrichment_engine import enrichment_engine
from app.services.rating_service import rating_service

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

