"""
SQLite database operations for storing text chunks and embeddings.

Manages database initialization, CRUD operations, and vector storage.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np
from src.config import Config


class Database:
    """SQLite database handler for chunks and embeddings."""

    def __init__(self, db_path: str = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or Config.DB_PATH
        self.connection = None
        self.cursor = None

    def connect(self) -> None:
        """Establish database connection."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        print(f"✅ Connected to database: {self.db_path}")

    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print(f"✅ Disconnected from database")

    def initialize_schema(self) -> None:
        """Create database schema."""
        # Chunks table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT NOT NULL,
            content TEXT NOT NULL,
            page_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Embeddings table (store vectors as BLOB)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk_id INTEGER NOT NULL UNIQUE,
            embedding BLOB NOT NULL,
            model_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chunk_id) REFERENCES chunks(id) ON DELETE CASCADE
        )
        """)

        # Metadata table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.connection.commit()
        print("✅ Database schema initialized")

    def add_chunk(self, section: str, content: str, page_url: str = None) -> int:
        """
        Add a text chunk to the database.

        Args:
            section: Section/title of the chunk
            content: Text content
            page_url: Source URL (optional)

        Returns:
            Chunk ID
        """
        self.cursor.execute(
            """
            INSERT INTO chunks (section, content, page_url)
            VALUES (?, ?, ?)
            """,
            (section, content, page_url)
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def add_embedding(self, chunk_id: int, embedding: np.ndarray, model_name: str) -> int:
        """
        Store embedding vector for a chunk.

        Args:
            chunk_id: ID of the chunk
            embedding: Embedding vector (numpy array)
            model_name: Name of the embedding model

        Returns:
            Embedding record ID
        """
        embedding_bytes = embedding.astype(np.float32).tobytes()
        self.cursor.execute(
            """
            INSERT INTO embeddings (chunk_id, embedding, model_name)
            VALUES (?, ?, ?)
            """,
            (chunk_id, embedding_bytes, model_name)
        )
        self.connection.commit()
        return self.cursor.lastrowid

    def get_chunk(self, chunk_id: int) -> Optional[Dict]:
        """Retrieve a chunk by ID."""
        self.cursor.execute("SELECT * FROM chunks WHERE id = ?", (chunk_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all_chunks(self, limit: int = None) -> List[Dict]:
        """Retrieve all chunks."""
        query = "SELECT * FROM chunks"
        if limit:
            query += f" LIMIT {limit}"
        self.cursor.execute(query)
        return [dict(row) for row in self.cursor.fetchall()]

    def get_embedding(self, chunk_id: int) -> Optional[Tuple[int, np.ndarray]]:
        """
        Retrieve embedding vector for a chunk.

        Args:
            chunk_id: ID of the chunk

        Returns:
            Tuple of (embedding_id, embedding_vector) or None
        """
        self.cursor.execute(
            "SELECT id, embedding FROM embeddings WHERE chunk_id = ?",
            (chunk_id,)
        )
        row = self.cursor.fetchone()
        if row:
            embedding_id, embedding_bytes = row[0], row[1]
            embedding_vector = np.frombuffer(embedding_bytes, dtype=np.float32)
            return embedding_id, embedding_vector
        return None

    def get_all_embeddings(self) -> List[Tuple[int, np.ndarray]]:
        """Retrieve all embeddings."""
        self.cursor.execute("""
            SELECT e.chunk_id, e.embedding
            FROM embeddings e
            ORDER BY e.chunk_id
        """)
        results = []
        for chunk_id, embedding_bytes in self.cursor.fetchall():
            embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
            results.append((chunk_id, embedding))
        return results

    def get_chunk_count(self) -> int:
        """Get total number of chunks."""
        self.cursor.execute("SELECT COUNT(*) FROM chunks")
        return self.cursor.fetchone()[0]

    def get_embedding_count(self) -> int:
        """Get total number of embeddings."""
        self.cursor.execute("SELECT COUNT(*) FROM embeddings")
        return self.cursor.fetchone()[0]

    def set_metadata(self, key: str, value: str) -> None:
        """Set metadata key-value pairs."""
        self.cursor.execute(
            """
            INSERT OR REPLACE INTO metadata (key, value)
            VALUES (?, ?)
            """,
            (key, value)
        )
        self.connection.commit()

    def get_metadata(self, key: str) -> Optional[str]:
        """Get metadata value by key."""
        self.cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def delete_chunk(self, chunk_id: int) -> bool:
        """Delete a chunk (cascades to embeddings)."""
        self.cursor.execute("DELETE FROM chunks WHERE id = ?", (chunk_id,))
        self.connection.commit()
        return self.cursor.rowcount > 0

    def clear_all(self) -> None:
        """Clear all data (use with caution!)."""
        self.cursor.execute("DELETE FROM embeddings")
        self.cursor.execute("DELETE FROM chunks")
        self.cursor.execute("DELETE FROM metadata")
        self.connection.commit()
        print("⚠️ All data cleared from database")


# Convenience functions
def init_database(db_path: str = None) -> Database:
    """Initialize and return a database connection."""
    db = Database(db_path)
    db.connect()
    db.initialize_schema()
    return db
