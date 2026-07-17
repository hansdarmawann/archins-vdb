# Module Usage Guide

Complete guide for using the Python modules in the `src/` directory.

## Quick Examples

### 1. Configuration Management

```python
from src.config import Config

# Display all configuration
Config.display()

# Access individual settings
print(Config.DB_PATH)
print(Config.EMBEDDING_MODEL)
print(Config.SEARCH_TOP_K)

# Validate configuration
if Config.validate():
    print("✅ Configuration is valid")
```

### 2. Database Operations

```python
from src.database import Database, init_database
import numpy as np

# Initialize database
db = init_database("../data/linux_docs.db")

# Add a text chunk
chunk_id = db.add_chunk(
    section="Installation",
    content="How to install Arch Linux...",
    page_url="https://wiki.archlinux.org/..."
)

# Add embedding
embedding = np.random.rand(384).astype(np.float32)  # Replace with actual embedding
db.add_embedding(chunk_id, embedding, model_name="BAAI/bge-small-en-v1.5")

# Retrieve data
chunk = db.get_chunk(chunk_id)
print(chunk)

# Get statistics
print(f"Total chunks: {db.get_chunk_count()}")
print(f"Total embeddings: {db.get_embedding_count()}")

# Close connection
db.disconnect()
```

### 3. Web Crawling

```python
from src.crawler import WebCrawler, crawl_archlinux_docs

# Initialize crawler
crawler = WebCrawler()

# Fetch single page
html = crawler.fetch_page("https://wiki.archlinux.org/index.php")

# Save to file
filepath = crawler.save_page("https://wiki.archlinux.org/...", html)

# Extract links
links = crawler.extract_links(html, base_url="https://wiki.archlinux.org")

# Crawl multiple pages
urls = ["url1", "url2", "url3"]
results = crawler.crawl_pages(urls, save_files=True)

# Recursive crawl (be careful with rate limiting!)
results = crawler.crawl_recursive(
    start_url="https://wiki.archlinux.org",
    max_pages=50,
    max_depth=2
)

# Helper function
results = crawl_archlinux_docs(max_pages=100)
```

### 4. Text Processing

```python
from src.text_processor import TextProcessor

# Convert HTML to Markdown
html = "<h1>Title</h1><p>Content</p>"
markdown = TextProcessor.html_to_markdown(html)

# Clean text
text = "Some  text   with   lots of   spaces"
cleaned = TextProcessor.clean_text(text)

# Extract sections
sections = TextProcessor.extract_sections(markdown)
for title, content in sections:
    print(f"Section: {title}")
    print(content[:100])

# Process HTML file
processed_text = TextProcessor.process_html_file("./data/raw/page.html")

# Batch process files
results = TextProcessor.batch_process_files("./data/raw/")
for filename, text in results:
    print(f"{filename}: {len(text)} characters")
```

### 5. Text Chunking

```python
from src.chunking import TextChunker, chunk_text

# Initialize chunker
chunker = TextChunker(
    min_size=200,
    max_size=1000,
    overlap=100
)

# Different chunking strategies
text = "Long document text..."

# By sentences
chunks = chunker.chunk_by_sentences(text)

# By paragraphs
chunks = chunker.chunk_by_paragraphs(text)

# By sections (Markdown)
sections = chunker.chunk_by_sections(text)
for section_title, section_content in sections:
    print(f"{section_title}: {len(section_content)} chars")

# Smart chunking (automatic selection)
chunks = chunker.smart_chunk(text)

# Convenience function
chunks = chunk_text(text, strategy="smart")
```

### 6. Embedding Generation

```python
from src.embeddings import (
    EmbeddingGenerator,
    EmbeddingCache,
    get_embedding_generator,
    encode_text,
    encode_texts
)
import numpy as np

# Initialize generator
generator = EmbeddingGenerator(
    model_name="BAAI/bge-small-en-v1.5",
    device="cpu",  # or "cuda"
    batch_size=32
)

# Encode single text
text = "How to install Arch Linux"
embedding = generator.encode(text, normalize=True)
print(f"Embedding shape: {embedding.shape}")

# Encode multiple texts
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = generator.encode(texts, normalize=True)

# Batch processing with progress bar
embeddings = generator.encode_batch(texts, show_progress=True)

# Calculate similarity
emb1 = generator.encode("Text A", normalize=True)[0]
emb2 = generator.encode("Text B", normalize=True)[0]
similarity = generator.similarity(emb1, emb2)
print(f"Similarity: {similarity:.4f}")

# Batch similarity
scores = generator.batch_similarity(emb1, embeddings)

# Get embedding dimension
dim = generator.get_dimension()
print(f"Embedding dimension: {dim}")

# Using global generator instance
embedding = encode_text("Some text")
embeddings = encode_texts(["Text 1", "Text 2"])

# Caching
cache = EmbeddingCache()
cache.set("key1", embedding)
retrieved = cache.get("key1")
```

### 7. Semantic Search & Retrieval

```python
from src.retrieval import SemanticSearch, semantic_search

# Initialize search engine
search = SemanticSearch(db_path="../data/linux_docs.db")

# Semantic search (top-5 similar documents)
query = "How do I partition the disk?"
results = search.retrieve(query, top_k=5, threshold=0.3)

for idx, doc in enumerate(results, 1):
    print(f"{idx}. {doc['section']} (score: {doc['score']:.4f})")
    print(f"   {doc['content'][:100]}...")

# Search by ID (find similar documents)
similar = search.retrieve_by_id(query_id=42, top_k=5)

# Batch search
queries = ["Query 1", "Query 2", "Query 3"]
batch_results = search.batch_retrieve(queries, top_k=5)

# Get statistics
stats = search.get_stats()
print(stats)

# Close connection
search.close()

# Convenient one-liner
results = semantic_search(
    query="How to install Arch?",
    db_path="../data/linux_docs.db",
    top_k=5
)
```

### 8. RAG Service

```python
from src.rag_service import RAGService, RAGPipeline, rag_answer

# Initialize RAG service
rag = RAGService(db_path="../data/linux_docs.db")

# Get service status
status = rag.get_status()
print(status)

# Retrieve context for a query
query = "How do I partition the disk during installation?"
documents = rag.retrieve_context(query, top_k=5)

# Format context for LLM
context = rag.format_context(documents)
print(context)

# Build LLM prompt
prompt = rag.build_prompt(query, context)
print(prompt)

# Generate answer (returns prompt-ready response)
result = rag.generate_answer(query, top_k=5)
print(result)

# Close service
rag.close()

# Using RAG Pipeline (higher-level interface)
pipeline = RAGPipeline(db_path="../data/linux_docs.db")
result = pipeline.process_query("How do I install packages?", top_k=5)
pipeline.close()

# Simple one-liner
result = rag_answer(
    query="How do I dual boot?",
    db_path="../data/linux_docs.db",
    top_k=5
)
```

## Complete Workflow Example

```python
from src.database import init_database
from src.crawler import WebCrawler
from src.text_processor import TextProcessor
from src.chunking import TextChunker
from src.embeddings import EmbeddingGenerator
from src.retrieval import SemanticSearch
from src.rag_service import RAGService

# 1. Initialize database
db = init_database()

# 2. Crawl pages
crawler = WebCrawler()
pages = [("https://example.com/page1.html", "<html>...</html>")]

# 3. Process and chunk
chunker = TextChunker()
embedder = EmbeddingGenerator()

for url, html in pages:
    # Convert to markdown
    markdown = TextProcessor.html_to_markdown(html)
    
    # Chunk text
    chunks = chunker.smart_chunk(markdown)
    
    # Store and embed
    for chunk in chunks:
        chunk_id = db.add_chunk(
            section="Example",
            content=chunk,
            page_url=url
        )
        
        embedding = embedder.encode(chunk, normalize=True)[0]
        db.add_embedding(chunk_id, embedding, "BAAI/bge-small-en-v1.5")

db.disconnect()

# 4. Search
search = SemanticSearch()
results = search.retrieve("How to install?", top_k=5)
search.close()

# 5. RAG
rag = RAGService()
answer = rag.generate_answer("How to install?", top_k=5)
rag.close()

print(answer)
```

## Error Handling

```python
from src.database import Database
from src.retrieval import SemanticSearch

try:
    # Database operations
    db = Database()
    db.connect()
    
    # Search operations
    search = SemanticSearch()
    results = search.retrieve("query")
    
    if not results:
        print("No results found")
    
    search.close()
    db.disconnect()
    
except Exception as e:
    print(f"Error: {e}")
    # Handle error appropriately
```

## Performance Tips

1. **Batch processing**: Use `encode_batch()` instead of individual encoding
2. **Caching**: Use `EmbeddingCache` for repeated queries
3. **GPU acceleration**: Set `EMBEDDING_DEVICE=cuda` in `.env`
4. **Batch size**: Adjust `EMBEDDING_BATCH_SIZE` based on available memory
5. **Database indexing**: Add indexes for frequently queried columns
6. **Chunking strategy**: Choose appropriate strategy for your data (sections vs. paragraphs)

## Debugging

```python
from src.config import Config

# Display configuration
Config.display()

# Check database
from src.database import Database
db = Database()
db.connect()
print(f"Chunks in DB: {db.get_chunk_count()}")
print(f"Embeddings in DB: {db.get_embedding_count()}")
db.disconnect()

# Test embedding model
from src.embeddings import EmbeddingGenerator
gen = EmbeddingGenerator()
emb = gen.encode("Test text")
print(f"Embedding dimension: {emb.shape}")
```

---

For more information, see individual module docstrings with `help()`:

```python
from src import config, database, crawler, text_processor, chunking, embeddings, retrieval, rag_service
help(config.Config)
help(database.Database)
# etc.
```
