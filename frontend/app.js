// API Base URL
const API_BASE = '/api';

// Global state
let currentAnswer = null;
let currentQuery = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadDocuments();
    checkHealth();
    setupDragAndDrop();
});

// Check API health
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        console.log('API Health:', data);
    } catch (error) {
        console.error('API health check failed:', error);
    }
}

// Upload documents (multiple files)
async function uploadDocuments(selectedFiles = null) {
    console.log('uploadDocuments() called');

    const fileInput = document.getElementById('fileInput');
    const files = selectedFiles ? Array.from(selectedFiles) : Array.from(fileInput.files);

    console.log('Files selected:', files.length, files.map(f => f.name));

    if (files.length === 0) {
        console.log('No files selected, returning');
        return;
    }

    // Show selected files
    const selectedFilesDiv = document.getElementById('selectedFiles');
    selectedFilesDiv.innerHTML = `📎 Selected: ${files.map(f => f.name).join(', ')}`;

    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.innerHTML = `<div class="loading">⏳ Uploading ${files.length} file(s)...</div>`;

    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
        console.log('Added file to FormData:', file.name);
    });

    try {
        console.log('Sending request to:', `${API_BASE}/documents/upload-multiple`);

        const response = await fetch(`${API_BASE}/documents/upload-multiple`, {
            method: 'POST',
            body: formData
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Upload failed:', errorData);
            throw new Error(errorData.detail || 'Upload failed');
        }

        const data = await response.json();
        console.log('Upload response:', data);

        // Build status message
        let statusHTML = '';

        console.log('Successful uploads:', data.successful_uploads.length);
        console.log('Failed uploads:', data.failed_uploads.length);

        if (data.successful_uploads && data.successful_uploads.length > 0) {
            const totalChunks = data.successful_uploads.reduce((sum, doc) => sum + doc.chunks_created, 0);
            statusHTML += `
                <div style="color: #10b981; padding: 12px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; margin-bottom: 10px;">
                    ✅ Successfully uploaded ${data.total_uploaded} file(s)! Created ${totalChunks} chunks total.
                    <ul style="margin-top: 8px; margin-left: 20px; font-size: 0.9em;">
                        ${data.successful_uploads.map(doc => `
                            <li>${doc.filename} (${doc.chunks_created} chunks)</li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }

        if (data.failed_uploads.length > 0) {
            statusHTML += `
                <div style="color: #ef4444; padding: 12px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px;">
                    ❌ Failed to upload ${data.total_failed} file(s):
                    <ul style="margin-top: 8px; margin-left: 20px; font-size: 0.9em;">
                        ${data.failed_uploads.map(fail => `
                            <li><strong>${fail.filename}</strong>: ${fail.error}</li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }

        statusDiv.innerHTML = statusHTML;

        // Reload documents list
        loadDocuments();

        // Clear file input and selected files display
        fileInput.value = '';
        selectedFilesDiv.innerHTML = '';

        // Clear status after 5 seconds if all successful
        if (data.failed_uploads.length === 0) {
            setTimeout(() => {
                statusDiv.innerHTML = '';
            }, 5000);
        }

    } catch (error) {
        // Check if it's an API key error
        const isApiKeyError = error.message.includes('401') ||
                             error.message.includes('API key') ||
                             error.message.includes('Unauthorized');

        if (isApiKeyError) {
            showApiKeyWarning();
        }

        statusDiv.innerHTML = `
            <div style="color: #ef4444; padding: 12px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px;">
                ❌ Upload failed: ${error.message}
                ${isApiKeyError ? `
                    <br><small style="margin-top: 8px; display: block; opacity: 0.8;">
                        💡 <strong>Action Required:</strong> Configure your OpenAI API key in the .env file (see SETUP_API_KEY.md)
                    </small>
                ` : ''}
            </div>
        `;
    }
}

// Show API key warning banner
function showApiKeyWarning() {
    const warningBanner = document.getElementById('apiKeyWarning');
    if (warningBanner) {
        warningBanner.style.display = 'block';
    }
}

// Load documents list
async function loadDocuments() {
    const listDiv = document.getElementById('documentsList');
    const countSpan = document.getElementById('docCount');
    
    try {
        const response = await fetch(`${API_BASE}/documents`);
        const data = await response.json();
        
        countSpan.textContent = data.total_count;
        
        if (data.documents.length === 0) {
            listDiv.innerHTML = '<p style="color: #666; text-align: center;">No documents yet</p>';
            return;
        }
        
        listDiv.innerHTML = data.documents.map(doc => `
            <div class="document-item">
                <div>
                    <strong>${doc.filename}</strong><br>
                    <small style="color: #666;">
                        ${formatFileSize(doc.file_size)} • ${doc.chunks_count} chunks
                    </small>
                </div>
                <button class="delete-btn" onclick="deleteDocument('${doc.document_id}')">
                    Delete
                </button>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading documents:', error);
        listDiv.innerHTML = '<p style="color: #f44336;">Error loading documents</p>';
    }
}

// Delete document
async function deleteDocument(docId) {
    if (!confirm('Are you sure you want to delete this document?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/documents/${docId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Delete failed');
        }

        loadDocuments();

    } catch (error) {
        alert('Failed to delete document: ' + error.message);
    }
}

// Delete all documents
async function deleteAllDocuments() {
    const docCount = document.getElementById('docCount').textContent;

    if (docCount === '0') {
        alert('No documents to delete');
        return;
    }

    const confirmed = confirm(
        `⚠️ WARNING: This will permanently delete ALL ${docCount} document(s) from your knowledge base.\n\n` +
        `This action CANNOT be undone!\n\n` +
        `Are you absolutely sure you want to continue?`
    );

    if (!confirmed) {
        return;
    }

    // Double confirmation for safety
    const doubleConfirm = confirm(
        `🚨 FINAL CONFIRMATION\n\n` +
        `You are about to delete ${docCount} document(s).\n\n` +
        `Click OK to proceed with deletion.`
    );

    if (!doubleConfirm) {
        return;
    }

    try {
        console.log('Deleting all documents...');

        const deleteBtn = document.getElementById('deleteAllBtn');
        const originalText = deleteBtn.innerHTML;
        deleteBtn.innerHTML = '⏳ Deleting...';
        deleteBtn.disabled = true;

        const response = await fetch(`${API_BASE}/documents/all`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Delete all failed');
        }

        const data = await response.json();
        console.log('Delete all response:', data);

        // Show success message
        alert(
            `✅ ${data.message}\n\n` +
            `Deleted: ${data.deleted_count} document(s)\n` +
            (data.failed_count > 0 ? `Failed: ${data.failed_count} document(s)` : '')
        );

        // Reload documents list
        loadDocuments();

        // Reset button
        deleteBtn.innerHTML = originalText;
        deleteBtn.disabled = false;

    } catch (error) {
        console.error('Failed to delete all documents:', error);
        alert('❌ Failed to delete all documents: ' + error.message);

        // Reset button
        const deleteBtn = document.getElementById('deleteAllBtn');
        deleteBtn.innerHTML = '🗑️ Delete All';
        deleteBtn.disabled = false;
    }
}

// Search knowledge base
async function searchKnowledgeBase() {
    const query = document.getElementById('searchQuery').value.trim();
    const resultsDiv = document.getElementById('results');

    if (!query) {
        alert('Please enter a question');
        return;
    }

    currentQuery = query;
    resultsDiv.innerHTML = '<div class="loading">🤔 Thinking...</div>';

    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                enable_auto_enrichment: true  // Always enabled - auto-enriches only when needed
            })
        });
        
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        const data = await response.json();
        currentAnswer = data.answer;
        displayResults(data);
        
    } catch (error) {
        resultsDiv.innerHTML = `
            <div style="color: #f44336; padding: 15px;">
                ❌ Search failed: ${error.message}
            </div>
        `;
    }
}

// Display search results
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    
    const confidencePercent = (data.confidence * 100).toFixed(0);
    const confidenceBadge = data.confidence >= 0.7 ? 'badge-success' : 
                           data.confidence >= 0.4 ? 'badge-warning' : 'badge-danger';
    
    const completeBadge = data.is_complete ? 
        '<span class="badge badge-success">Complete</span>' : 
        '<span class="badge badge-warning">Incomplete</span>';
    
    let html = `
        <div class="answer-section">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="color: #c7d2fe; font-size: 1.3em;">Answer</h3>
                <div>
                    ${completeBadge}
                    <span class="badge ${confidenceBadge}">${confidencePercent}% Confident</span>
                </div>
            </div>

            <div class="confidence-bar">
                <div class="confidence-fill" style="width: ${confidencePercent}%"></div>
            </div>

            <p style="margin-top: 15px; line-height: 1.8; color: #e4e4e7; font-size: 1.05em;">${data.answer}</p>
    `;
    
    // Auto-enrichment info
    if (data.auto_enrichment_applied) {
        html += `
            <div style="margin-top: 15px; padding: 16px; background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15)); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 10px; color: #a5b4fc; font-size: 0.95em;">
                🌐 <strong style="color: #c7d2fe;">Auto-enriched</strong> with information from: <span style="color: #e0e7ff;">${data.auto_enrichment_sources.join(', ')}</span>
            </div>
        `;
    }
    
    // Sources
    if (data.sources && data.sources.length > 0) {
        html += `
            <div class="sources">
                <h4 style="color: #c7d2fe; margin-bottom: 10px;">📚 Sources</h4>
                ${data.sources.map(source => {
                    const isExternal = source.metadata && source.metadata.enriched;
                    const sourceUrl = source.metadata && source.metadata.url;
                    const sourceType = source.metadata && source.metadata.source;

                    return `
                        <div class="source-item">
                            <strong style="color: #e4e4e7;">
                                ${isExternal ? '🌐 ' : '📄 '}${source.document_name}
                            </strong>
                            <span class="badge badge-success" style="margin-left: 10px;">
                                ${(source.relevance_score * 100).toFixed(0)}% relevant
                            </span>
                            ${isExternal ? `
                                <span class="badge badge-warning" style="margin-left: 5px;">
                                    External Source
                                </span>
                            ` : ''}
                            <p style="margin-top: 8px; color: #a1a1aa; font-size: 0.9em; line-height: 1.5;">
                                ${source.content.substring(0, 200)}...
                            </p>
                            ${sourceUrl ? `
                                <a href="${sourceUrl}" target="_blank" rel="noopener noreferrer"
                                   style="color: #60a5fa; text-decoration: none; font-size: 0.85em; margin-top: 6px; display: inline-block;">
                                    🔗 View Full Source
                                </a>
                            ` : ''}
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }
    
    // Missing info and enrichment suggestions
    if (!data.is_complete && data.missing_info && data.missing_info.length > 0) {
        html += `
            <div class="enrichment-suggestions">
                <h4 style="color: #fbbf24; margin-bottom: 10px;">💡 Missing Information</h4>
                <ul style="margin-left: 20px; color: #e4e4e7;">
                    ${data.missing_info.map(info => `<li style="margin: 8px 0;">${info}</li>`).join('')}
                </ul>
        `;

        if (data.enrichment_suggestions && data.enrichment_suggestions.length > 0) {
            html += `
                <h4 style="color: #fbbf24; margin-top: 15px; margin-bottom: 10px;">
                    🎯 Enrichment Suggestions
                </h4>
                ${data.enrichment_suggestions.map(suggestion => `
                    <div class="suggestion-item">
                        <strong style="color: #c7d2fe;">${suggestion.type}</strong> <span style="color: #a1a1aa;">(${suggestion.priority} priority)</span><br>
                        <span style="color: #d4d4d8; margin-top: 4px; display: block;">${suggestion.suggestion}</span>
                        ${suggestion.external_source_url ? `
                            <br>
                            <a href="${suggestion.external_source_url}" target="_blank" rel="noopener noreferrer"
                               style="color: #60a5fa; text-decoration: none; font-size: 0.9em; margin-top: 6px; display: inline-block;">
                                🔗 View Source
                            </a>
                        ` : ''}
                    </div>
                `).join('')}
            `;
        }

        html += `</div>`;
    }
    
    // Rating section
    html += `
        <div class="rating-section">
            <h4 style="color: #c7d2fe; margin-bottom: 10px;">⭐ Rate this answer</h4>
            <div class="stars" id="ratingStars">
                ${[1, 2, 3, 4, 5].map(i => `
                    <span class="star" data-rating="${i}" onclick="rateAnswer(${i})">★</span>
                `).join('')}
            </div>
            <div id="ratingFeedback" style="margin-top: 10px;"></div>
        </div>
    `;
    
    html += `</div>`;
    
    resultsDiv.innerHTML = html;
}

// Rate answer
async function rateAnswer(rating) {
    if (!currentAnswer || !currentQuery) return;
    
    // Update star display
    const stars = document.querySelectorAll('.star');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
    
    try {
        const response = await fetch(`${API_BASE}/rate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: currentQuery,
                answer: currentAnswer,
                rating: rating
            })
        });
        
        if (!response.ok) {
            throw new Error('Rating failed');
        }
        
        document.getElementById('ratingFeedback').innerHTML = `
            <div style="color: #4caf50;">✅ Thank you for your feedback!</div>
        `;
        
    } catch (error) {
        document.getElementById('ratingFeedback').innerHTML = `
            <div style="color: #f44336;">❌ Failed to save rating</div>
        `;
    }
}

// Utility: Format file size
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Setup drag and drop
function setupDragAndDrop() {
    const uploadSection = document.querySelector('.upload-section');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadSection.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadSection.addEventListener(eventName, () => {
            uploadSection.style.borderColor = 'rgba(139, 92, 246, 0.8)';
            uploadSection.style.background = 'rgba(99, 102, 241, 0.15)';
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadSection.addEventListener(eventName, () => {
            uploadSection.style.borderColor = 'rgba(99, 102, 241, 0.4)';
            uploadSection.style.background = 'rgba(99, 102, 241, 0.05)';
        }, false);
    });

    uploadSection.addEventListener('drop', (e) => {
        const files = e.dataTransfer?.files;
        if (files && files.length > 0) {
            uploadDocuments(files);
        }
    }, false);
}
