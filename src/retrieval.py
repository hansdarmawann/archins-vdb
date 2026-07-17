"""
Semantic search and retrieval using embeddings.

Performs similarity-based retrieval of relevant text chunks.
"""

import sqlite3
import numpy as np
from typing import List, Dict, Tuple
from src.config import Config
from src.embeddings import EmbeddingGenerator, get_embedding_generator


class SemanticSearch:
    """Semantic search engine for retrieving similar documents."""

    def __init__(self, db_path: str = None, embedding_generator: EmbeddingGenerator = None):
        """
        Initialize semantic search.

        Args:
            db_path: Path to SQLite database
            embedding_generator: EmbeddingGenerator instance
        """
        self.db_path = db_path or Config.DB_PATH
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.embedding_gen = embedding_generator or get_embedding_generator()

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()

    def retrieve(
        self,
        query: str,
        top_k: int = None,
        threshold: float = None
    ) -> List[Dict]:
        """
        Retrieve top-k similar documents for a query.

        Args:
            query: Query text
            top_k: Number of results to return
            threshold: Minimum similarity threshold

        Returns:
            List of retrieved documents with scores
        """
        top_k = top_k or Config.SEARCH_TOP_K
        threshold = threshold or Config.SIMILARITY_THRESHOLD

        # Encode query
        query_embedding = self.embedding_gen.encode(query, normalize=True)[0]

        # Fetch all embeddings and chunks
        self.cursor.execute("""
            SELECT e.chunk_id, e.embedding, c.section, c.content, c.page_url
            FROM embeddings e
            JOIN chunks c ON e.chunk_id = c.id
        """)

        results = []

        # Compare with all documents
        for row in self.cursor.fetchall():
            chunk_id = row["chunk_id"]
            embedding_bytes = row["embedding"]
            section = row["section"]
            content = row["content"]
            page_url = row["page_url"]

            # Convert bytes to numpy array
            doc_embedding = np.frombuffer(embedding_bytes, dtype=np.float32)

            # Calculate similarity
            similarity_score = float(np.dot(query_embedding, doc_embedding))

            if similarity_score >= threshold:
                results.append({
                    "chunk_id": chunk_id,
                    "section": section,
                    "content": content,
                    "page_url": page_url,
                    "score": similarity_score
                })

        # Sort by similarity score and return top-k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def retrieve_by_id(self, query_id: int, top_k: int = None, threshold: float = None) -> List[Dict]:
        """
        Retrieve similar documents for a document in the database.

        Args:
            query_id: ID of the chunk to use as query
            top_k: Number of results to return
            threshold: Minimum similarity threshold

        Returns:
            List of retrieved documents with scores
        """
        # Get the query document's content and embedding
        self.cursor.execute("""
            SELECT c.content, e.embedding
            FROM chunks c
            JOIN embeddings e ON c.id = e.chunk_id
            WHERE c.id = ?
        """, (query_id,))

        row = self.cursor.fetchone()
        if not row:
            return []

        content = row["content"]
        query_embedding = np.frombuffer(row["embedding"], dtype=np.float32)

        # Search for similar documents
        top_k = top_k or Config.SEARCH_TOP_K
        threshold = threshold or Config.SIMILARITY_THRESHOLD

        self.cursor.execute("""
            SELECT e.chunk_id, e.embedding, c.section, c.content, c.page_url
            FROM embeddings e
            JOIN chunks c ON e.chunk_id = c.id
            WHERE c.id != ?
        """, (query_id,))

        results = []

        for row in self.cursor.fetchall():
            doc_embedding = np.frombuffer(row["embedding"], dtype=np.float32)
            similarity_score = float(np.dot(query_embedding, doc_embedding))

            if similarity_score >= threshold:
                results.append({
                    "chunk_id": row["chunk_id"],
                    "section": row["section"],
                    "content": row["content"],
                    "page_url": row["page_url"],
                    "score": similarity_score
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def batch_retrieve(
        self,
        queries: List[str],
        top_k: int = None
    ) -> List[List[Dict]]:
        """
        Retrieve results for multiple queries.

        Args:
            queries: List of query texts
            top_k: Number of results per query

        Returns:
            List of result lists
        """
        results = []
        for query in queries:
            result = self.retrieve(query, top_k=top_k)
            results.append(result)
        return results

    def get_stats(self) -> Dict:
        """Get retrieval statistics."""
        self.cursor.execute("SELECT COUNT(*) FROM chunks")
        chunk_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM embeddings")
        embedding_count = self.cursor.fetchone()[0]

        return {
            "total_chunks": chunk_count,
            "total_embeddings": embedding_count,
            "embedding_model": self.embedding_gen.model_name,
            "embedding_dimension": self.embedding_gen.get_dimension()
        }


# Convenience function
def semantic_search(query: str, db_path: str = None, top_k: int = None) -> List[Dict]:
    """
    Simple semantic search interface.

    Args:
        query: Query text
        db_path: Path to database
        top_k: Number of results

    Returns:
        List of retrieved documents
    """
    search = SemanticSearch(db_path)
    results = search.retrieve(query, top_k=top_k)
    search.close()
    return results
