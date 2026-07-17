"""
Text processing utilities for converting HTML to clean Markdown.

Handles HTML parsing, content extraction, and markdown conversion.
"""

from bs4 import BeautifulSoup
from typing import Optional, List
import re
import trafilatura
from pathlib import Path


class TextProcessor:
    """Process and clean HTML content."""

    @staticmethod
    def html_to_markdown(html: str, include_links: bool = True) -> str:
        """
        Convert HTML to clean Markdown text.

        Args:
            html: HTML content
            include_links: Whether to include links

        Returns:
            Markdown text
        """
        # Try using trafilatura first (optimized for article extraction)
        try:
            content = trafilatura.extract(
                html,
                include_links=include_links,
                output_format="markdown"
            )
            if content:
                return content
        except Exception as e:
            print(f"⚠️ Trafilatura extraction failed: {e}")

        # Fallback to BeautifulSoup
        return TextProcessor._fallback_html_to_markdown(html)

    @staticmethod
    def _fallback_html_to_markdown(html: str) -> str:
        """Fallback method using BeautifulSoup."""
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text(separator="\n")

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        text = "\n".join(line for line in lines if line)

        return text

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r"\n\n+", "\n\n", text)
        text = re.sub(r" +", " ", text)

        # Remove special characters but keep markdown
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)

        # Normalize quotes
        text = text.replace("'", "'").replace(""", '"').replace(""", '"')

        return text.strip()

    @staticmethod
    def extract_sections(text: str) -> List[tuple]:
        """
        Extract sections from text.

        Args:
            text: Markdown formatted text

        Returns:
            List of (section_title, section_content) tuples
        """
        sections = []
        current_section = "Introduction"
        current_content = []

        for line in text.split("\n"):
            if line.startswith("#"):
                # Found a heading
                if current_content:
                    sections.append((current_section, "\n".join(current_content)))
                    current_content = []
                current_section = line.lstrip("#").strip()
            else:
                current_content.append(line)

        # Add last section
        if current_content:
            sections.append((current_section, "\n".join(current_content)))

        return [(title, content.strip()) for title, content in sections if content.strip()]

    @staticmethod
    def process_html_file(filepath: str) -> str:
        """
        Process an HTML file and return cleaned text.

        Args:
            filepath: Path to HTML file

        Returns:
            Cleaned markdown text
        """
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()

        markdown = TextProcessor.html_to_markdown(html)
        cleaned = TextProcessor.clean_text(markdown)
        return cleaned

    @staticmethod
    def batch_process_files(directory: str) -> List[tuple]:
        """
        Process all HTML files in a directory.

        Args:
            directory: Path to directory with HTML files

        Returns:
            List of (filename, processed_text) tuples
        """
        results = []
        path = Path(directory)

        for html_file in path.glob("*.html"):
            try:
                text = TextProcessor.process_html_file(str(html_file))
                results.append((html_file.name, text))
            except Exception as e:
                print(f"❌ Failed to process {html_file}: {e}")

        return results
