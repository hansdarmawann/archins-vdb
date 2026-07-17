# Archins-VDB: Building a RAG System with Arch Linux Documentation

A comprehensive, step-by-step tutorial for building a complete **Retrieval-Augmented Generation (RAG)** system from scratch. This project demonstrates how to crawl documentation, process text, generate embeddings, and create a semantic search service with LLM integration.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Workflow Steps](#workflow-steps)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This project builds a RAG system that allows you to:
1. **Crawl** Arch Linux documentation from the web
2. **Convert** HTML content to clean Markdown text
3. **Chunk** text into semantic chunks for better retrieval
4. **Generate** embeddings using sentence transformers
5. **Retrieve** relevant contexts based on semantic similarity
6. **Generate** answers using LLM with retrieved context

The entire system is designed to be educational and production-ready, with each step documented in a Jupyter notebook.

## 🏗️ Architecture

```
Web Documentation
        ↓
    [Crawler] → HTML pages
        ↓
[HTML to Markdown] → Clean text
        ↓
    [Chunking] → Text segments
        ↓
  [Embeddings] → Vector database (SQLite)
        ↓
  [Retrieval] → Semantic search
        ↓
  [RAG Service] → LLM + Context → Answer
```

## ✅ Prerequisites

- **Python**: 3.11 or higher
- **pip** or **conda** for package management
- **SQLite**: Usually pre-installed with Python
- **LLM API** (optional): For Step 9 (OpenAI, Anthropic, or local models)
- **4GB+ RAM**: For embedding models

## 📦 Installation

### 1. Clone or Download the Repository

```bash
cd /Users/u1/Documents/archins-vdb
```

### 2. Create and Activate Virtual Environment

```bash
# Using venv
python3 -m venv venv
source venv/bin/activate

# Or using conda
conda create -n archins-vdb python=3.11
conda activate archins-vdb
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env with your settings
# (optional: add LLM API keys if using Step 9)
```

## 📂 Project Structure

```
archins-vdb/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
│
├── notebooks/                         # Jupyter notebooks (move here)
│   ├── Step_1_Project_Setup.ipynb
│   ├── Step_2_SQLite_Database.ipynb
│   ├── Step_3_Web_Crawler.ipynb
│   ├── Step_4_HTML_to_Markdown.ipynb
│   ├── Step_5_Markdown_Chunking.ipynb
│   ├── Step_6_Generate_Embeddings.ipynb
│   ├── Step_7_Semantic_Search.ipynb
│   ├── Step_8_Mini_RAG.ipynb
│   └── Step_9_RAG_Service_Prototype.ipynb
│
├── src/                               # Python modules (reusable code)
│   ├── __init__.py
│   ├── config.py                      # Configuration settings
│   ├── database.py                    # SQLite database operations
│   ├── crawler.py                     # Web crawler implementation
│   ├── text_processor.py              # HTML to Markdown conversion
│   ├── chunking.py                    # Text chunking logic
│   ├── embeddings.py                  # Embedding generation
│   ├── retrieval.py                   # Semantic search/retrieval
│   └── rag_service.py                 # RAG service implementation
│
├── data/                              # Data storage
│   ├── raw/                           # Raw crawled HTML files
│   └── linux_docs.db                  # SQLite vector database
│
└── logs/                              # (Optional) Log files
```

## 🚀 Getting Started

### Quick Start (5 minutes)

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Run Step 1 (Project Setup) in Jupyter
jupyter notebook notebooks/Step_1_Project_Setup.ipynb

# 3. Follow the notebooks in order from Step 1 to Step 9
```

### Running Notebooks

```bash
# Start Jupyter Lab (recommended)
jupyter lab

# Or start Jupyter Notebook
jupyter notebook
```

Then navigate to `notebooks/` and open each step in order.

## 📚 Workflow Steps

| Step | Notebook | Description | Output |
|------|----------|-------------|--------|
| 1 | `Step_1_Project_Setup.ipynb` | Verify Python version, install dependencies, create folder structure | Project ready |
| 2 | `Step_2_SQLite_Database.ipynb` | Initialize SQLite database schema for chunks and embeddings | `data/linux_docs.db` |
| 3 | `Step_3_Web_Crawler.ipynb` | Crawl Arch Linux documentation from the web | HTML files in `data/raw/` |
| 4 | `Step_4_HTML_to_Markdown.ipynb` | Convert HTML to clean Markdown text | Markdown content |
| 5 | `Step_5_Markdown_Chunking.ipynb` | Split Markdown into semantic chunks | Chunks stored in database |
| 6 | `Step_6_Generate_Embeddings.ipynb` | Generate embeddings using SentenceTransformer | Vector embeddings in database |
| 7 | `Step_7_Semantic_Search.ipynb` | Perform semantic search using embeddings | Top-K similar chunks |
| 8 | `Step_8_Mini_RAG.ipynb` | Build RAG pipeline: retrieve + prompt | LLM-ready context |
| 9 | `Step_9_RAG_Service_Prototype.ipynb` | Create REST API service | Running service |

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# Database
DB_PATH=./data/linux_docs.db

# Crawler
CRAWLER_TIMEOUT=10
MAX_RETRIES=3
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Embeddings
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_BATCH_SIZE=32
EMBEDDING_DEVICE=cpu  # or 'cuda' for GPU

# Retrieval
SEARCH_TOP_K=5
SIMILARITY_THRESHOLD=0.3

# LLM (Optional for Step 9)
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.7

# Service
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8000
```

### Example .env Setup

```bash
cat .env.example > .env
# Edit .env with your preferred settings
nano .env
```

## 🔧 Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | Latest | HTTP requests for web crawling |
| `beautifulsoup4` | Latest | HTML parsing |
| `lxml` | Latest | Fast XML/HTML processing |
| `trafilatura` | Latest | Content extraction from HTML |
| `sentence-transformers` | Latest | Embedding generation |
| `sqlite3` | Built-in | Vector database |
| `numpy` | Latest | Vector operations |
| `python-dotenv` | Latest | Environment variable management |
| `tqdm` | Latest | Progress bars |

## 📖 Usage Examples

### Using the RAG System Programmatically

```python
from src.retrieval import SemanticSearch
from src.rag_service import RAGService

# Initialize retrieval
search = SemanticSearch("../data/linux_docs.db")

# Retrieve relevant contexts
question = "How do I partition the disk during Arch Linux installation?"
contexts = search.retrieve(question, top_k=5)

# Use with RAG service
rag = RAGService()
answer = rag.generate_answer(question, contexts)
print(answer)
```

### Running the Service

```bash
# From notebooks/Step_9_RAG_Service_Prototype.ipynb
# Or run: python -m src.rag_service
```

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError for dependencies

**Solution**: Run `pip install -r requirements.txt` again

### Issue: Embedding model download hangs

**Solution**: Models are downloaded on first use. Check internet connection and ensure sufficient disk space (2-3 GB)

### Issue: SQLite database locked

**Solution**: Ensure no other processes are accessing the database. Close Jupyter kernels and restart.

### Issue: LLM API key error (Step 9)

**Solution**: Verify your API key in `.env` file and ensure it has necessary permissions

### Issue: Out of memory during embedding generation

**Solution**: Reduce `EMBEDDING_BATCH_SIZE` in `.env` or use `EMBEDDING_DEVICE=cpu`

## 📝 Notes

- **First Run**: Initial runs will download embedding models (~400MB) and crawl documentation, which may take 15-30 minutes
- **Database**: SQLite is suitable for this project size. For larger datasets, consider PostgreSQL with pgvector
- **GPU Support**: To use GPU for embeddings, install `torch` with CUDA support and set `EMBEDDING_DEVICE=cuda`
- **Production**: For production use, refactor notebooks into proper services with error handling, logging, and monitoring

## 🤝 Contributing

Improvements and extensions are welcome:
- Add more data sources beyond Arch Linux
- Implement other embedding models
- Add REST API endpoints for production
- Improve chunking strategy with semantic aware splitting

## 📄 License

Open source for educational purposes.

## 🆘 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review individual notebook documentation
3. Check data/ folder for existing outputs

---

**Last Updated**: July 2026
**Python Version**: 3.11+
**Status**: Educational & Production Ready