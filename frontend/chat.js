// Global state
let currentSessionId = null;
let sessions = [];
let documentCount = 0;
let documents = [];
const API_BASE = 'http://localhost:8000/api';

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadSessions();
    await loadDocumentCount();
    
    // Auto-resize textarea
    const textarea = document.getElementById('messageInput');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
});

// Load all sessions
async function loadSessions() {
    try {
        const response = await fetch(`${API_BASE}/sessions`);
        sessions = await response.json();
        
        const sessionsList = document.getElementById('sessionsList');
        
        if (sessions.length === 0) {
            sessionsList.innerHTML = '<p style="color: #999; font-size: 14px;">No sessions yet. Create one!</p>';
            return;
        }
        
        sessionsList.innerHTML = sessions.map(session => `
            <div class="session-item ${session.session_id === currentSessionId ? 'active' : ''}" 
                 onclick="selectSession('${session.session_id}')">
                <div class="session-name">${escapeHtml(session.name)}</div>
                <div class="session-meta">${session.message_count} messages</div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

// Create new session
async function createNewSession() {
    try {
        const response = await fetch(`${API_BASE}/sessions`, {
            method: 'POST'
        });
        
        const session = await response.json();
        currentSessionId = session.session_id;
        
        await loadSessions();
        await loadConversationHistory(currentSessionId);
        
    } catch (error) {
        console.error('Error creating session:', error);
        showError('Failed to create new session');
    }
}

// Select a session
async function selectSession(sessionId) {
    currentSessionId = sessionId;
    await loadSessions();
    await loadConversationHistory(sessionId);
}

// Load conversation history
async function loadConversationHistory(sessionId) {
    try {
        const response = await fetch(`${API_BASE}/sessions/${sessionId}/messages`);
        const data = await response.json();
        
        const messagesContainer = document.getElementById('messagesContainer');
        messagesContainer.innerHTML = '';
        
        if (!data.messages || data.messages.length === 0) {
            messagesContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">💬</div>
                    <h3>Start a Conversation</h3>
                    <p>Ask me anything! Auto-Enrich will search the web when your documents don't have the answer.</p>
                </div>
            `;
            return;
        }
        
        data.messages.forEach(msg => {
            addMessageToUI(msg.role, msg.content, {
                confidence: msg.confidence,
                webSearchUsed: msg.web_search_used,
                sources: msg.sources
            });
        });
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
    } catch (error) {
        console.error('Error loading conversation:', error);
    }
}

// Send message
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message || !currentSessionId) return;
    
    const autoEnrich = document.getElementById('autoEnrichToggle').checked;
    
    // Clear input
    input.value = '';
    input.style.height = 'auto';
    
    // Add user message to UI
    addMessageToUI('user', message);
    
    // Show loading
    const loadingId = showLoading();
    
    // Disable send button
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: message,
                enable_web_search: autoEnrich,  // Web search is now part of auto-enrich
                enable_auto_enrichment: autoEnrich
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to send message');
        }
        
        const data = await response.json();
        
        // Remove loading
        removeLoading(loadingId);
        
        // Add assistant message
        addMessageToUI('assistant', data.message.content, {
            confidence: data.message.confidence,
            webSearchUsed: data.message.web_search_used,
            sources: data.message.sources
        });
        
        // Update session list
        await loadSessions();
        
    } catch (error) {
        console.error('Error sending message:', error);
        removeLoading(loadingId);
        showError('Failed to send message. Please try again.');
    } finally {
        sendBtn.disabled = false;
    }
}

// Add message to UI
function addMessageToUI(role, content, meta = {}) {
    const messagesContainer = document.getElementById('messagesContainer');
    
    // Remove empty state if present
    const emptyState = messagesContainer.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = role === 'user' ? '👤' : '🤖';
    const avatarClass = role === 'user' ? 'user-avatar' : 'assistant-avatar';
    
    let metaHtml = '';
    if (role === 'assistant' && meta.confidence !== undefined) {
        const confidenceClass = meta.confidence >= 0.7 ? 'confidence-high' : 
                               meta.confidence >= 0.4 ? 'confidence-medium' : 'confidence-low';
        const confidenceText = meta.confidence >= 0.7 ? 'High' : 
                              meta.confidence >= 0.4 ? 'Medium' : 'Low';
        
        metaHtml = `
            <div class="message-meta">
                <span class="confidence-badge ${confidenceClass}">Confidence: ${confidenceText}</span>
                ${meta.webSearchUsed ? '<span class="web-search-badge">🌐 Web Search</span>' : ''}
            </div>
        `;
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar ${avatarClass}">${avatar}</div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(content)}</div>
            ${metaHtml}
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Show loading indicator
function showLoading() {
    const messagesContainer = document.getElementById('messagesContainer');
    const loadingDiv = document.createElement('div');
    const loadingId = 'loading-' + Date.now();
    loadingDiv.id = loadingId;
    loadingDiv.className = 'message assistant';
    loadingDiv.innerHTML = `
        <div class="message-avatar assistant-avatar">🤖</div>
        <div class="message-content">
            <div class="message-text loading">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return loadingId;
}

// Remove loading indicator
function removeLoading(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// Load document count
async function loadDocumentCount() {
    try {
        const response = await fetch(`${API_BASE}/documents`);
        const data = await response.json();
        documentCount = data.total_count;
        document.getElementById('docCount').textContent = `${documentCount} documents uploaded`;
    } catch (error) {
        console.error('Error loading document count:', error);
        document.getElementById('docCount').textContent = 'Error loading count';
    }
}

// Upload documents
async function uploadDocuments() {
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    
    if (files.length === 0) return;
    
    const uploadStatus = document.getElementById('uploadStatus');
    uploadStatus.textContent = `Uploading ${files.length} file(s)...`;
    uploadStatus.style.color = '#2196F3';
    
    const formData = new FormData();
    for (let file of files) {
        formData.append('files', file);
    }
    
    try {
        const response = await fetch(`${API_BASE}/documents/upload-multiple`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.total_uploaded > 0 && result.total_failed === 0) {
            uploadStatus.textContent = `✓ ${result.total_uploaded} uploaded successfully`;
            uploadStatus.style.color = '#4CAF50';
        } else if (result.total_uploaded > 0 && result.total_failed > 0) {
            uploadStatus.textContent = `⚠️ ${result.total_uploaded} uploaded, ${result.total_failed} failed`;
            uploadStatus.style.color = '#FF9800';
        } else {
            uploadStatus.textContent = `❌ All ${result.total_failed} uploads failed`;
            uploadStatus.style.color = '#f44336';
        }
        
        // Update document count
        await loadDocumentCount();
        
        // Clear file input
        fileInput.value = '';
        
        // Show detailed results
        if (result.total_uploaded > 0) {
            const fileNames = result.successful_uploads.map(u => u.filename).join(', ');
            showSuccess(`Successfully uploaded: ${fileNames}`);
        }
        
        if (result.total_failed > 0) {
            const failedNames = result.failed_uploads.map(f => `${f.filename}: ${f.error}`).join('\n');
            showError(`Failed uploads:\n${failedNames}`);
        }
        
        // Reset status color after 5 seconds
        setTimeout(() => {
            uploadStatus.style.color = '#666';
        }, 5000);
        
    } catch (error) {
        console.error('Error uploading documents:', error);
        uploadStatus.textContent = '❌ Upload failed';
        uploadStatus.style.color = '#f44336';
        showError('Failed to upload documents');
    }
}

// Handle Enter key
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function showError(message) {
    // Simple alert for now - could be replaced with a toast notification
    console.error('Error:', message);
}

function showSuccess(message) {
    // Simple alert for now - could be replaced with a toast notification
    console.log('Success:', message);
}

// Documents Modal Functions
function openDocumentsModal() {
    const modal = document.getElementById('documentsModal');
    modal.classList.add('active');
    loadDocumentsList();
}

function closeDocumentsModal() {
    const modal = document.getElementById('documentsModal');
    modal.classList.remove('active');
}

async function loadDocumentsList() {
    const container = document.getElementById('documentsListModal');

    try {
        const response = await fetch(`${API_BASE}/documents`);
        const data = await response.json();
        documents = data.documents;

        if (documents.length === 0) {
            container.innerHTML = `
                <div class="no-documents">
                    <div class="no-documents-icon">📄</div>
                    <p>No documents uploaded yet</p>
                    <p style="font-size: 14px; margin-top: 10px;">Click "Upload Documents" to add files</p>
                </div>
            `;
            return;
        }

        container.innerHTML = documents.map(doc => `
            <div class="document-item" id="doc-${doc.document_id}">
                <div class="document-info">
                    <div class="document-name">📄 ${escapeHtml(doc.filename)}</div>
                    <div class="document-meta">
                        ${formatFileSize(doc.file_size)} •
                        ${doc.chunks_count} chunks •
                        Uploaded ${formatDate(doc.upload_timestamp)}
                    </div>
                </div>
                <div class="document-actions">
                    <button class="delete-doc-btn" onclick="deleteDocument('${doc.document_id}', '${escapeHtml(doc.filename)}')">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error('Error loading documents:', error);
        container.innerHTML = `
            <div class="no-documents">
                <div class="no-documents-icon">⚠️</div>
                <p>Failed to load documents</p>
            </div>
        `;
    }
}

async function deleteDocument(documentId, filename) {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
        return;
    }

    const docElement = document.getElementById(`doc-${documentId}`);
    const deleteBtn = docElement.querySelector('.delete-doc-btn');

    // Disable button and show loading
    deleteBtn.disabled = true;
    deleteBtn.textContent = 'Deleting...';

    try {
        const response = await fetch(`${API_BASE}/documents/${documentId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete document');
        }

        // Fade out and remove
        docElement.style.opacity = '0';
        docElement.style.transform = 'translateX(-20px)';

        setTimeout(() => {
            docElement.remove();

            // Update document count
            loadDocumentCount();

            // Check if no documents left
            const remaining = document.querySelectorAll('.document-item').length;
            if (remaining === 0) {
                loadDocumentsList();
            }
        }, 300);

        showSuccess(`Deleted "${filename}"`);

    } catch (error) {
        console.error('Error deleting document:', error);
        showError('Failed to delete document');

        // Re-enable button
        deleteBtn.disabled = false;
        deleteBtn.textContent = '🗑️ Delete';
    }
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('documentsModal');
    if (e.target === modal) {
        closeDocumentsModal();
    }
});

