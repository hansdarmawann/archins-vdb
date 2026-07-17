"""
Embedding generation using sentence transformers.

Converts text chunks into dense vector embeddings for semantic search.
"""

import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from src.config import Config


class EmbeddingGenerator:
    """Generate embeddings for text using sentence transformers."""

    def __init__(self, model_name: str = None, device: str = None, batch_size: int = None):
        """
        Initialize embedding generator.

        Args:
            model_name: Name of the sentence transformer model
            device: Device to use ('cpu' or 'cuda')
            batch_size: Batch size for processing
        """
        self.model_name = model_name or Config.EMBEDDING_MODEL
        self.device = device or Config.EMBEDDING_DEVICE
        self.batch_size = batch_size or Config.EMBEDDING_BATCH_SIZE
        
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name, device=self.device)
        print(f"✅ Model loaded (device: {self.device})")

    def encode(self, texts: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Encode text(s) into embeddings.

        Args:
            texts: Single text or list of texts
            normalize: Whether to normalize embeddings (L2 normalization)

        Returns:
            Embedding vector(s) as numpy array
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=normalize,
            convert_to_numpy=True
        )

        return embeddings

    def encode_batch(self, texts: List[str], show_progress: bool = True) -> List[np.ndarray]:
        """
        Encode multiple texts with progress bar.

        Args:
            texts: List of texts to encode
            show_progress: Whether to show progress bar

        Returns:
            List of embedding vectors
        """
        iterator = tqdm(texts, desc="Encoding") if show_progress else texts
        embeddings = []

        for text in iterator:
            embedding = self.encode(text, normalize=True)
            embeddings.append(embedding[0])

        return embeddings

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.model.get_sentence_embedding_dimension()

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score (0-1)
        """
        return float(np.dot(embedding1, embedding2))

    def batch_similarity(
        self,
        query_embedding: np.ndarray,
        embeddings: List[np.ndarray]
    ) -> np.ndarray:
        """
        Compute similarity between query and multiple embeddings.

        Args:
            query_embedding: Query embedding vector
            embeddings: List of embedding vectors

        Returns:
            Array of similarity scores
        """
        embeddings_array = np.array(embeddings)
        scores = np.dot(embeddings_array, query_embedding)
        return scores


class EmbeddingCache:
    """Cache for storing computed embeddings."""

    def __init__(self):
        """Initialize embedding cache."""
        self.cache = {}

    def get(self, key: str) -> Union[np.ndarray, None]:
        """Get embedding from cache."""
        return self.cache.get(key)

    def set(self, key: str, embedding: np.ndarray) -> None:
        """Store embedding in cache."""
        self.cache[key] = embedding

    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()

    def size(self) -> int:
        """Get cache size."""
        return len(self.cache)


# Global embedding generator instance
_embedding_generator = None


def get_embedding_generator(
    model_name: str = None,
    device: str = None,
    batch_size: int = None
) -> EmbeddingGenerator:
    """
    Get or create global embedding generator instance.

    Args:
        model_name: Name of the model
        device: Device to use
        batch_size: Batch size

    Returns:
        EmbeddingGenerator instance
    """
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator(model_name, device, batch_size)
    return _embedding_generator


def encode_text(text: str) -> np.ndarray:
    """Convenience function to encode text using global generator."""
    generator = get_embedding_generator()
    return generator.encode(text, normalize=True)[0]


def encode_texts(texts: List[str]) -> List[np.ndarray]:
    """Convenience function to encode multiple texts."""
    generator = get_embedding_generator()
    embeddings = generator.encode(texts, normalize=True)
    return [emb for emb in embeddings]
