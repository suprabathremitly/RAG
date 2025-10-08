# AI-Powered Knowledge Base with RAG

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.1.0-orange.svg)](CHANGELOG_V2.1.md)

A production-ready Retrieval-Augmented Generation (RAG) system that combines document search with AI-powered question answering. Features intelligent auto-enrichment from trusted external sources, session-based conversations, and a modern chat interface.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Development](#development)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This AI Knowledge Base enables you to:

- **Upload documents** (PDF, TXT, DOCX) and build a searchable knowledge base
- **Ask questions** in natural language and receive AI-generated answers
- **Automatic enrichment** from Wikipedia, arXiv, and PubMed when your documents lack information
- **Session management** for organizing conversations
- **Multi-document upload** for efficient batch processing
- **Source attribution** with confidence scoring for transparency

### Technology Stack

- **Backend**: FastAPI (Python 3.9+)
- **Vector Database**: ChromaDB
- **AI Models**: OpenAI GPT-5-Mini, text-embedding-3-small
- **Frontend**: Vanilla JavaScript with modern UI
- **Storage**: File-based with JSON sessions

---

## Key Features

### 🎯 Core Capabilities

| Feature | Description |
|---------|-------------|
| **Document Processing** | Upload and process PDF, TXT, DOCX files with automatic chunking |
| **Semantic Search** | Vector-based similarity search using OpenAI embeddings |
| **AI Answers** | GPT-5-Mini powered responses with source citations |
| **Confidence Scoring** | 0.0-1.0 confidence scale for answer reliability |
| **Session Management** | Organize conversations with persistent history |

### ⚡ Advanced Features

| Feature | Description |
|---------|-------------|
| **Auto-Enrichment** | Automatically fetches missing information from trusted sources |
| **Multi-Document Upload** | Batch upload with progress tracking |
| **Document Management** | View, search, and delete documents via modal interface |
| **Source Attribution** | Track both uploaded documents and external sources |
| **Web Search Integration** | Integrated into auto-enrichment for comprehensive answers |

### 🎨 User Experience

- **Claude-Style Chat Interface** - Modern, gradient-based UI with smooth animations
- **Real-Time Feedback** - Confidence badges, web search indicators, typing animations
- **Responsive Design** - Works seamlessly on desktop and mobile
- **Dark Theme** - Easy on the eyes with glassmorphism effects

---

## Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/suprabathremitly/RAG.git
cd RAG

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# 5. Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. Open in browser
# Navigate to: http://localhost:8000/chat.html
```

**That's it!** You now have a fully functional AI Knowledge Base running locally.

---

## Architecture

### System Overview

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│                    Frontend (chat.html)                  │
│  • Session Management  • Document Upload  • Chat UI     │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend (routes.py)             │
│  • REST API  • Session Manager  • Document Processor    │
└──────────────────────────┬──────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  ChromaDB   │   │   OpenAI    │   │ Enrichment  │
│  (Vectors)  │   │   (GPT-5)   │   │  (Wikipedia)│
└─────────────┘   └─────────────┘   └─────────────┘
```

### RAG Pipeline Flow

```
1. User Query
   ↓
2. Embed Query (OpenAI text-embedding-3-small)
   ↓
3. Vector Search (ChromaDB - Top 5 similar chunks)
   ↓
4. Generate Answer (GPT-5-Mini with context)
   ↓
5. Assess Confidence (0.0 - 1.0 scale)
   ↓
6. Auto-Enrich? (If confidence < 0.7)
   ├─ Yes → Fetch from Wikipedia/arXiv/PubMed
   │         ↓
   │      Re-generate Answer
   │         ↓
   └─ No  → Return Answer
```

### Key Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Server** | FastAPI | REST API, async request handling |
| **Vector Store** | ChromaDB | Semantic search, document embeddings |
| **LLM** | GPT-5-Mini | Answer generation, reasoning |
| **Embeddings** | text-embedding-3-small | Document and query vectorization |
| **Session Store** | JSON Files | Conversation persistence |
| **Enrichment** | Wikipedia API, arXiv, PubMed | External knowledge sources |

### Design Principles

1. **Modular Architecture** - Separation of concerns with service-based design
2. **Async Processing** - Non-blocking I/O for better performance
3. **Type Safety** - Pydantic models for validation and documentation
4. **Graceful Degradation** - System works even when external services fail
5. **Cost Optimization** - Auto-enrichment only when needed (confidence < 0.7)

---

## Installation

### Prerequisites

- **Python**: 3.9 or higher
- **OpenAI API Key**: Get one from [OpenAI Platform](https://platform.openai.com/)
- **Disk Space**: 2GB minimum for dependencies and data
- **RAM**: 4GB minimum recommended

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/suprabathremitly/RAG.git
cd RAG
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies include:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `langchain` - LLM framework
- `chromadb` - Vector database
- `openai` - OpenAI API client
- `pypdf` - PDF processing
- `python-docx` - DOCX processing
- `pydantic-settings` - Configuration management

#### 4. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Required configuration:**

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here

# LLM Configuration
LLM_MODEL=gpt-5-mini-2025-08-07
LLM_TEMPERATURE=0.1
MAX_TOKENS=2000

# Vector Store Configuration
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# Document Storage
UPLOAD_DIRECTORY=./data/uploads

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=5
CONFIDENCE_THRESHOLD=0.7
```

#### 5. Create Data Directories

```bash
mkdir -p data/uploads data/chroma_db data/sessions
```

#### 6. Start the Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Server will start at:**
- **Chat Interface**: http://localhost:8000/chat.html
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

### Verification

Check if the server is running correctly:

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Expected response:
# {"status":"healthy","version":"2.1.0","vector_store_status":"healthy","documents_count":0}
```

---

## Configuration

### Environment Variables

All configuration is managed through the `.env` file. Here's a complete reference:

#### OpenAI Configuration

```bash
# Your OpenAI API key (required)
OPENAI_API_KEY=sk-your-key-here
```

#### LLM Configuration

```bash
# Model selection (recommended: gpt-5-mini-2025-08-07)
LLM_MODEL=gpt-5-mini-2025-08-07

# Temperature (0.0 = deterministic, 1.0 = creative)
LLM_TEMPERATURE=0.1

# Maximum tokens in response
MAX_TOKENS=2000
```

**Model Options:**
- `gpt-5-mini-2025-08-07` - **Recommended** - Fast, cost-effective, optimized for chat
- `gpt-4-turbo-preview` - More powerful, higher cost
- `gpt-4o` - Latest, balanced performance

See [MODEL_UPDATE.md](MODEL_UPDATE.md) for detailed model comparison.

#### Storage Configuration

```bash
# Vector database directory
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# Uploaded documents directory
UPLOAD_DIRECTORY=./data/uploads
```

#### RAG Configuration

```bash
# Document chunk size (characters)
CHUNK_SIZE=1000

# Overlap between chunks (characters)
CHUNK_OVERLAP=200

# Number of similar chunks to retrieve
TOP_K_RESULTS=5

# Confidence threshold for auto-enrichment (0.0-1.0)
CONFIDENCE_THRESHOLD=0.7
```

#### API Configuration

```bash
# Server host
API_HOST=0.0.0.0

# Server port
API_PORT=8000
```

### Advanced Configuration

For production deployments, consider:

- **Increase `MAX_TOKENS`** for longer responses (default: 2000)
- **Adjust `CONFIDENCE_THRESHOLD`** to control auto-enrichment frequency (default: 0.7)
- **Modify `TOP_K_RESULTS`** for more/fewer context chunks (default: 5)
- **Change `CHUNK_SIZE`** based on document type (default: 1000)

---

## Usage

### Web Interface

#### 1. Access the Chat Interface

Open your browser and navigate to:
```
http://localhost:8000/chat.html
```

#### 2. Create a New Session

- Click **"+ New Chat"** in the sidebar
- A new conversation session will be created
- Each session maintains its own conversation history

#### 3. Upload Documents

**Single Upload:**
1. Click **"📤 Upload Documents"** in the sidebar
2. Select a file (PDF, TXT, or DOCX)
3. Click **"Upload"**
4. Wait for processing confirmation

**Multi-Upload:**
1. Click **"📤 Upload Documents"**
2. Select multiple files (Ctrl/Cmd + Click)
3. Click **"Upload"**
4. Track progress for each file

#### 4. Ask Questions

1. Type your question in the input box
2. Press **Enter** or click **Send**
3. View the AI-generated answer with:
   - **Confidence badge** (High/Medium/Low)
   - **Source citations** (documents or external sources)
   - **Web search indicator** (if auto-enrichment was used)

#### 5. Manage Documents

1. Click **"📄 View Documents"** in the sidebar
2. Browse your uploaded documents
3. View details: filename, size, chunks, upload date
4. Delete documents with confirmation

#### 6. Switch Between Sessions

- Click on any session in the sidebar
- View conversation history
- Continue previous conversations

### Auto-Enrichment

The system automatically enriches answers when:
- Confidence score is below 0.7
- Your documents don't contain sufficient information

**Enrichment Sources:**
1. **Wikipedia** - General knowledge
2. **arXiv** - Academic papers
3. **PubMed** - Medical research

**Example:**
```
You: "What is quantum computing?"
(If not in your documents)
→ System fetches from Wikipedia
→ Adds to knowledge base
→ Provides comprehensive answer
```

### Command Line Usage

#### Upload Document via API

```bash
curl -X POST "http://localhost:8000/api/documents/upload-multiple" \
  -F "files=@document1.pdf" \
  -F "files=@document2.txt"
```

#### Send Chat Message

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "message": "What is in my documents?",
    "enable_auto_enrichment": true
  }'
```

#### List Documents

```bash
curl http://localhost:8000/api/documents
```

#### Health Check

```bash
curl http://localhost:8000/api/health
```

---

## API Reference

### Base URL

```
http://localhost:8000
```

### Endpoints

#### Session Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/sessions` | Create new session |
| `GET` | `/api/sessions` | List all sessions |
| `GET` | `/api/sessions/{id}` | Get session details |
| `GET` | `/api/sessions/{id}/messages` | Get conversation history |
| `DELETE` | `/api/sessions/{id}` | Delete session |

#### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send message and get AI response |

**Request Body:**
```json
{
  "session_id": "string",
  "message": "string",
  "enable_auto_enrichment": true
}
```

**Response:**
```json
{
  "session_id": "string",
  "message": {
    "role": "assistant",
    "content": "string",
    "timestamp": "2025-10-07T20:00:00",
    "sources": [...],
    "confidence": 0.95,
    "web_search_used": false
  }
}
```

#### Document Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents/upload-multiple` | Upload multiple documents |
| `GET` | `/api/documents` | List all documents |
| `GET` | `/api/documents/{id}` | Get document details |
| `DELETE` | `/api/documents/{id}` | Delete document |

#### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/docs` | Interactive API documentation (Swagger) |
| `GET` | `/` | Legacy web UI |
| `GET` | `/chat.html` | Modern chat interface |

### Interactive Documentation

Visit http://localhost:8000/docs for full interactive API documentation with:
- Request/response schemas
- Try-it-out functionality
- Authentication details
- Example requests

---

## Development

### Project Structure

```
RAG/
├── app/
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Configuration management
│   ├── models/
│   │   └── schemas.py               # Pydantic models and schemas
│   ├── services/
│   │   ├── document_processor.py    # Document parsing and chunking
│   │   ├── vector_store.py          # ChromaDB vector operations
│   │   ├── rag_pipeline.py          # RAG orchestration
│   │   ├── enrichment_engine.py     # External source enrichment
│   │   └── session_manager.py       # Session management
│   └── api/
│       └── routes.py                # API endpoint definitions
├── frontend/
│   ├── chat.html                    # Modern chat interface
│   ├── chat.js                      # Chat interface logic
│   ├── index.html                   # Legacy web UI
│   └── app.js                       # Legacy UI logic
├── data/
│   ├── uploads/                     # Uploaded documents storage
│   ├── chroma_db/                   # Vector database persistence
│   └── sessions/                    # Session data (JSON files)
├── tests/                           # Test suite (if available)
├── .env                             # Environment configuration (not in git)
├── .env.example                     # Example configuration
├── requirements.txt                 # Python dependencies
├── CHANGELOG_V2.1.md               # Version 2.1 changelog
├── MODEL_UPDATE.md                  # Model configuration guide
└── README.md                        # This file
```

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_document_processor.py -v
```

### Code Style

This project follows:
- **PEP 8** for Python code style
- **Type hints** for function signatures
- **Docstrings** for classes and functions
- **Pydantic models** for data validation

### Adding New Features

1. **Create a new service** in `app/services/`
2. **Define schemas** in `app/models/schemas.py`
3. **Add API endpoints** in `app/api/routes.py`
4. **Update frontend** in `frontend/chat.js`
5. **Write tests** in `tests/`
6. **Update documentation** in README.md
---

## Deployment

### Production Considerations

#### 1. Environment Setup

```bash
# Use production ASGI server
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 2. Security

- **API Key Management**: Use environment variables, never commit `.env`
- **CORS Configuration**: Update `app/main.py` for production domains
- **HTTPS**: Use reverse proxy (nginx) with SSL certificates
- **Rate Limiting**: Implement rate limiting for API endpoints

#### 3. Scaling

**Horizontal Scaling:**
- Deploy multiple instances behind a load balancer
- Use shared storage for `data/` directory (S3, NFS)
- Consider managed vector database (Pinecone, Weaviate)

**Vertical Scaling:**
- Increase server resources (CPU, RAM)
- Optimize `CHUNK_SIZE` and `TOP_K_RESULTS`
- Use faster embedding models

#### 4. Monitoring

```bash
# Add logging
import logging
logging.basicConfig(level=logging.INFO)

# Monitor endpoints
# - Response times
# - Error rates
# - API usage
# - Document count
```

#### 5. Backup

```bash
# Backup vector database
tar -czf chroma_backup.tar.gz data/chroma_db/

# Backup documents
tar -czf uploads_backup.tar.gz data/uploads/

# Backup sessions
tar -czf sessions_backup.tar.gz data/sessions/
```

### Docker Deployment (Coming Soon)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment

**Recommended Platforms:**
- **AWS**: EC2 + S3 + RDS
- **Google Cloud**: Cloud Run + Cloud Storage
- **Azure**: App Service + Blob Storage
- **Heroku**: Easy deployment with buildpacks

---

## Documentation

### Available Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | This file - comprehensive overview |
| [CHANGELOG_V2.1.md](CHANGELOG_V2.1.md) | Version 2.1 features and changes |
| [MODEL_UPDATE.md](MODEL_UPDATE.md) | Model configuration and comparison |
| `.env.example` | Configuration template |

### Additional Resources

- **API Documentation**: http://localhost:8000/docs (when server is running)
- **GitHub Repository**: https://github.com/suprabathremitly/RAG
- **OpenAI Documentation**: https://platform.openai.com/docs

---

## Troubleshooting

### Common Issues

#### 1. Server Won't Start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
kill -9 <PID>

# Or use different port
python -m uvicorn app.main:app --port 8001
```

#### 2. OpenAI API Errors

```bash
# Verify API key
echo $OPENAI_API_KEY

# Check .env file
cat .env | grep OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### 3. Document Upload Fails

- **Check file size**: Maximum 10MB per file
- **Check file format**: Only PDF, TXT, DOCX supported
- **Check disk space**: Ensure sufficient space in `data/uploads/`
- **Check permissions**: Ensure write access to `data/` directory

#### 4. Vector Search Returns No Results

```bash
# Check if documents are indexed
curl http://localhost:8000/api/documents

# Verify ChromaDB
ls -la data/chroma_db/

# Re-upload documents if needed
```

#### 5. Auto-Enrichment Not Working

- **Check confidence threshold**: Default is 0.7
- **Verify internet connection**: Required for Wikipedia, arXiv, PubMed
- **Check API rate limits**: OpenAI has rate limits
- **Enable in request**: Ensure `enable_auto_enrichment: true`

### Getting Help

1. **Check logs**: Server logs show detailed error messages
2. **Review documentation**: See [CHANGELOG_V2.1.md](CHANGELOG_V2.1.md)
3. **Open an issue**: https://github.com/suprabathremitly/RAG/issues
4. **Check API docs**: http://localhost:8000/docs

---

## Performance Optimization

### Tips for Better Performance

1. **Optimize Chunk Size**
   - Smaller chunks (500-800): Better for precise answers
   - Larger chunks (1000-1500): Better for context

2. **Adjust Top-K Results**
   - Fewer results (3-5): Faster, less context
   - More results (5-10): Slower, more context

3. **Model Selection**
   - `gpt-5-mini`: Fast, cost-effective (recommended)
   - `gpt-4-turbo`: More powerful, slower, expensive
   - `gpt-4o`: Balanced performance

4. **Caching**
   - ChromaDB caches embeddings automatically
   - Consider Redis for query caching in production

5. **Batch Processing**
   - Use multi-document upload for efficiency
   - Process documents during off-peak hours

---

## Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

1. **Report Bugs**: Open an issue with detailed description
2. **Suggest Features**: Share your ideas in issues
3. **Improve Documentation**: Fix typos, add examples
4. **Submit Code**: Create pull requests with new features
5. **Share Feedback**: Let us know how you're using the system

### Development Workflow

```bash
# 1. Fork the repository
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/RAG.git

# 3. Create a feature branch
git checkout -b feature/your-feature-name

# 4. Make your changes
# 5. Test your changes
pytest

# 6. Commit with clear message
git commit -m "Add: your feature description"

# 7. Push to your fork
git push origin feature/your-feature-name

# 8. Open a pull request
```

### Code Guidelines

- Follow PEP 8 style guide
- Add type hints to functions
- Write docstrings for classes and methods
- Include tests for new features
- Update documentation as needed

---

## License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 AI Knowledge Base

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Acknowledgments

This project is built with excellent open-source technologies:

- **[OpenAI](https://openai.com/)** - GPT models and embeddings
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern web framework
- **[ChromaDB](https://www.trychroma.com/)** - Vector database
- **[LangChain](https://www.langchain.com/)** - LLM framework
- **[Uvicorn](https://www.uvicorn.org/)** - ASGI server

Special thanks to the open-source community for making this possible.

---

## Contact & Support

- **GitHub Repository**: https://github.com/suprabathremitly/RAG
- **Issues**: https://github.com/suprabathremitly/RAG/issues
- **Discussions**: https://github.com/suprabathremitly/RAG/discussions

For questions, feedback, or support, please open an issue on GitHub.

---

## Version History

- **v2.1.0** (Current) - Simplified auto-enrichment, document management, GPT-5-Mini support
- **v2.0.0** - Session management, multi-document upload, Claude-style chat interface
- **v1.0.0** - Initial release with basic RAG functionality

See [CHANGELOG_V2.1.md](CHANGELOG_V2.1.md) for detailed version history.

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

**Built with ❤️ using AI and modern web technologies**

[Report Bug](https://github.com/suprabathremitly/RAG/issues) · [Request Feature](https://github.com/suprabathremitly/RAG/issues) · [Documentation](https://github.com/suprabathremitly/RAG)

</div>
