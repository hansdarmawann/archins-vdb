"""
Text chunking utilities for splitting documents into semantic chunks.

Handles various chunking strategies for optimal retrieval.
"""

from typing import List, Tuple
import re
from src.config import Config


class TextChunker:
    """Split text into semantic chunks."""

    def __init__(self, min_size: int = None, max_size: int = None, overlap: int = None):
        """
        Initialize chunker.

        Args:
            min_size: Minimum chunk size
            max_size: Maximum chunk size
            overlap: Overlap between chunks
        """
        self.min_size = min_size or Config.MIN_CHUNK_SIZE
        self.max_size = max_size or Config.MAX_CHUNK_SIZE
        self.overlap = overlap or Config.OVERLAP_SIZE

    def chunk_by_sentences(self, text: str) -> List[str]:
        """
        Split text into semantic chunks by sentences.

        Args:
            text: Input text

        Returns:
            List of chunks
        """
        # Split by sentences (simple approach)
        sentences = re.split(r"(?<=[.!?])\s+", text)

        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence)

            # Check if adding this sentence would exceed max size
            if current_size + sentence_size > self.max_size and current_chunk:
                # Save current chunk
                chunk_text = " ".join(current_chunk)
                chunks.append(chunk_text)

                # Start new chunk with overlap
                overlap_text = " ".join(current_chunk[-(self.overlap // len(current_chunk)):])
                current_chunk = [overlap_text] if overlap_text else []
                current_size = len(overlap_text)

            current_chunk.append(sentence)
            current_size += sentence_size + 1  # +1 for space

        # Add remaining text
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if len(chunk_text) >= self.min_size:
                chunks.append(chunk_text)

        return chunks

    def chunk_by_paragraphs(self, text: str) -> List[str]:
        """
        Split text into semantic chunks by paragraphs.

        Args:
            text: Input text with paragraph breaks (\n\n)

        Returns:
            List of chunks
        """
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_size = len(para)

            # Check if adding this paragraph exceeds max size
            if current_size + para_size > self.max_size and current_chunk:
                chunk_text = "\n\n".join(current_chunk)
                chunks.append(chunk_text)
                current_chunk = []
                current_size = 0

            if para_size < self.max_size:  # Only add if paragraph itself isn't too large
                current_chunk.append(para)
                current_size += para_size + 2  # +2 for newlines

        # Add remaining
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            if len(chunk_text) >= self.min_size:
                chunks.append(chunk_text)

        return chunks

    def chunk_by_sections(self, text: str, section_marker: str = "#") -> List[Tuple[str, str]]:
        """
        Split text into chunks by sections/headers.

        Args:
            text: Markdown formatted text
            section_marker: Markdown header marker (e.g., "#")

        Returns:
            List of (section_title, section_content) tuples
        """
        sections = []
        current_section = "Introduction"
        current_content = []

        for line in text.split("\n"):
            if line.startswith(section_marker):
                # Found a heading
                if current_content:
                    section_text = "\n".join(current_content).strip()
                    if len(section_text) >= self.min_size:
                        sections.append((current_section, section_text))
                    current_content = []

                current_section = line.lstrip(section_marker).strip()
            else:
                current_content.append(line)

        # Add last section
        if current_content:
            section_text = "\n".join(current_content).strip()
            if len(section_text) >= self.min_size:
                sections.append((current_section, section_text))

        # Further chunk large sections
        final_chunks = []
        for section_title, section_content in sections:
            if len(section_content) > self.max_size:
                sub_chunks = self.chunk_by_sentences(section_content)
                for sub_chunk in sub_chunks:
                    if len(sub_chunk) >= self.min_size:
                        final_chunks.append((section_title, sub_chunk))
            else:
                final_chunks.append((section_title, section_content))

        return final_chunks

    def smart_chunk(self, text: str, use_sections: bool = True) -> List[str]:
        """
        Smart chunking: use sections if available, else use paragraphs.

        Args:
            text: Input text
            use_sections: Whether to prioritize section-based chunking

        Returns:
            List of chunks
        """
        if use_sections and "#" in text:
            sections = self.chunk_by_sections(text)
            return [content for _, content in sections]
        elif "\n\n" in text:
            return self.chunk_by_paragraphs(text)
        else:
            return self.chunk_by_sentences(text)


def chunk_text(text: str, strategy: str = "smart") -> List[str]:
    """
    Convenience function for chunking text.

    Args:
        text: Input text
        strategy: 'sentences', 'paragraphs', 'sections', or 'smart'

    Returns:
        List of chunks
    """
    chunker = TextChunker()

    if strategy == "sentences":
        return chunker.chunk_by_sentences(text)
    elif strategy == "paragraphs":
        return chunker.chunk_by_paragraphs(text)
    elif strategy == "sections":
        sections = chunker.chunk_by_sections(text)
        return [content for _, content in sections]
    else:  # smart
        return chunker.smart_chunk(text)
