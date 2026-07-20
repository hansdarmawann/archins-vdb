# Project Structure Documentation

## Directory Layout

```
archins-rag/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── notebooks/
│   └── (Jupyter notebooks - Step 1 through Step 9)
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── crawler.py
│   ├── text_processor.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── retrieval.py
│   └── rag_service.py
│
├── data/
│   ├── raw/
│   └── linux_docs.db
│
└── logs/
    └── (Log files)
```

## File Descriptions

### Root Level

| File | Purpose |
|------|---------|
| `README.md` | Project documentation and getting started guide |
| `requirements.txt` | Python dependencies with versions |
| `.env.example` | Template for environment variables |
| `.gitignore` | Git ignore rules |

### `/notebooks`

Contains Jupyter notebooks for each step of the RAG pipeline:

- `Step_1_Project_Setup.ipynb` - Environment verification and setup
- `Step_2_SQLite_Database.ipynb` - Database initialization
- `Step_3_Web_Crawler.ipynb` - Web page crawling
- `Step_4_HTML_to_Markdown.ipynb` - HTML to Markdown conversion
- `Step_5_Markdown_Chunking.ipynb` - Text chunking
- `Step_6_Generate_Embeddings.ipynb` - Embedding generation
- `Step_7_Semantic_Search.ipynb` - Search implementation
- `Step_8_Mini_RAG.ipynb` - RAG pipeline demo
- `Step_9_RAG_Service_Prototype.ipynb` - Service prototype

### `/src` - Python Modules

| Module | Purpose |
|--------|---------|
| `__init__.py` | Package initialization, exports |
| `config.py` | Configuration management from environment |
| `database.py` | SQLite database operations |
| `crawler.py` | Web crawler implementation |
| `text_processor.py` | HTML parsing and Markdown conversion |
| `chunking.py` | Text chunking strategies |
| `embeddings.py` | Sentence embedding generation |
| `retrieval.py` | Semantic search and similarity retrieval |
| `rag_service.py` | RAG pipeline service |

### `/data`

- `raw/` - Storage for downloaded HTML files
- `linux_docs.db` - SQLite database with chunks and embeddings

### `/logs`

Application log files for debugging and monitoring.

## Module Dependencies

```
config.py (standalone - configuration)
    ↓
database.py (uses: config, sqlite3)
    ↓
crawler.py (uses: config, requests, BeautifulSoup)
    ↓
text_processor.py (uses: BeautifulSoup, trafilatura)
    ↓
chunking.py (uses: config, re)
    ↓
embeddings.py (uses: config, sentence-transformers, numpy)
    ↓
retrieval.py (uses: database, embeddings, numpy)
    ↓
rag_service.py (uses: retrieval, config)
```

## Data Flow

```
1. CRAWLING
   User → notebooks/Step_3 → crawler.py → data/raw/
   
2. PROCESSING
   data/raw/ → notebooks/Step_4 → text_processor.py → clean markdown
   
3. CHUNKING
   markdown → notebooks/Step_5 → chunking.py → text chunks
   
4. STORAGE
   chunks → database.py → data/linux_docs.db
   
5. EMBEDDING
   chunks → notebooks/Step_6 → embeddings.py → vectors in DB
   
6. RETRIEVAL
   query → retrieval.py → semantic_search → ranked results
   
7. RAG
   results → rag_service.py → prompt building → LLM ready
```

## Configuration

Environment variables are loaded from `.env` and managed by `config.py`:

- Database settings
- Crawler parameters
- Embedding model configuration
- LLM settings
- Service configuration
- Logging settings

See `.env.example` for all available options.

## Database Schema

```sql
-- Chunks table
CREATE TABLE chunks (
    id INTEGER PRIMARY KEY,
    section TEXT,
    content TEXT,
    page_url TEXT,
    created_at TIMESTAMP
)

-- Embeddings table
CREATE TABLE embeddings (
    id INTEGER PRIMARY KEY,
    chunk_id INTEGER UNIQUE,
    embedding BLOB,
    model_name TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (chunk_id) REFERENCES chunks(id)
)

-- Metadata table
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP
)
```

## Python Version & Dependencies

- **Python**: 3.11+
- **Key packages**: torch, sentence-transformers, requests, beautifulsoup4, trafilatura, numpy
- See `requirements.txt` for complete list

## Quick Import Reference

```python
# Configuration
from src.config import Config

# Database
from src.database import Database, init_database

# Crawling
from src.crawler import WebCrawler

# Text Processing
from src.text_processor import TextProcessor

# Chunking
from src.chunking import TextChunker, chunk_text

# Embeddings
from src.embeddings import EmbeddingGenerator, encode_text, encode_texts

# Retrieval
from src.retrieval import SemanticSearch, semantic_search

# RAG Service
from src.rag_service import RAGService, RAGPipeline, rag_answer
```

---

For more details, see README.md or individual module docstrings.
