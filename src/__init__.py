"""
Archins-rag: Retrieval-Augmented Generation System

A comprehensive package for building RAG systems with web documentation.
"""

__version__ = "1.0.0"
__author__ = "Archins VDB Contributors"

from src.config import Config
from src.database import Database
from src.crawler import WebCrawler
from src.text_processor import TextProcessor
from src.chunking import TextChunker
from src.embeddings import EmbeddingGenerator
from src.retrieval import SemanticSearch
from src.rag_service import RAGService

__all__ = [
    "Config",
    "Database",
    "WebCrawler",
    "TextProcessor",
    "TextChunker",
    "EmbeddingGenerator",
    "SemanticSearch",
    "RAGService",
]
