#!/usr/bin/env python3
"""
Script to reprocess documents that have 0 chunks.
This is useful when documents were uploaded before the API key was configured.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStoreService
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def reprocess_documents():
    """Reprocess all documents that have 0 chunks."""
    
    doc_processor = DocumentProcessor()
    vector_store = VectorStoreService()
    
    # Get all documents
    upload_dir = Path(settings.upload_directory)
    
    if not upload_dir.exists():
        logger.error(f"Upload directory not found: {upload_dir}")
        return
    
    # Find all uploaded files
    files = list(upload_dir.glob("*"))
    logger.info(f"Found {len(files)} files in upload directory")
    
    reprocessed = 0
    failed = 0
    
    for file_path in files:
        if not file_path.is_file():
            continue
            
        # Extract document ID and filename from the file path
        # Format: {doc_id}_{filename}
        filename = file_path.name
        parts = filename.split('_', 1)
        
        if len(parts) < 2:
            logger.warning(f"Skipping file with unexpected name format: {filename}")
            continue
            
        doc_id = parts[0]
        original_filename = parts[1]
        
        # Check if document already has chunks
        try:
            chunks = vector_store.get_document_chunks(doc_id)
            if chunks and len(chunks) > 0:
                logger.info(f"✓ {original_filename} already has {len(chunks)} chunks, skipping")
                continue
        except Exception as e:
            logger.debug(f"Could not check chunks for {doc_id}: {e}")
        
        # Reprocess the document
        logger.info(f"⏳ Reprocessing {original_filename}...")
        
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Extract text and create chunks
            text = doc_processor._extract_text(file_path)
            
            if not text or len(text.strip()) == 0:
                logger.warning(f"❌ No text extracted from {original_filename}")
                failed += 1
                continue
            
            # Create metadata
            metadata = {
                'document_id': doc_id,
                'filename': original_filename,
                'file_path': str(file_path),
                'file_size': len(content),
                'file_type': file_path.suffix.lower(),
            }
            
            # Chunk the document
            chunks = doc_processor._chunk_document(text, metadata)
            
            if not chunks:
                logger.warning(f"❌ No chunks created for {original_filename}")
                failed += 1
                continue
            
            # Add to vector store
            await vector_store.add_documents(chunks)
            
            logger.info(f"✅ Successfully reprocessed {original_filename} - created {len(chunks)} chunks")
            reprocessed += 1
            
        except Exception as e:
            logger.error(f"❌ Error reprocessing {original_filename}: {e}")
            failed += 1
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Reprocessing complete!")
    logger.info(f"✅ Successfully reprocessed: {reprocessed} documents")
    logger.info(f"❌ Failed: {failed} documents")
    logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    print("🔄 Starting document reprocessing...")
    print("This will reprocess all documents that have 0 chunks.\n")
    
    asyncio.run(reprocess_documents())
    
    print("\n✨ Done! Your documents should now be searchable.")

