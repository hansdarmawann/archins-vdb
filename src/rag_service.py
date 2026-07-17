"""
RAG (Retrieval-Augmented Generation) service implementation.

Combines retrieval and LLM prompting for question answering.
"""

from typing import List, Dict, Optional
from src.retrieval import SemanticSearch
from src.config import Config


class RAGService:
    """Retrieval-Augmented Generation service."""

    def __init__(self, db_path: str = None):
        """
        Initialize RAG service.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path or Config.DB_PATH
        self.search = SemanticSearch(db_path)
        self.llm_provider = Config.LLM_PROVIDER
        self.llm_model = Config.LLM_MODEL

    def retrieve_context(
        self,
        query: str,
        top_k: int = None
    ) -> List[Dict]:
        """
        Retrieve relevant context for a query.

        Args:
            query: User query
            top_k: Number of results to retrieve

        Returns:
            List of relevant documents
        """
        return self.search.retrieve(query, top_k=top_k)

    def format_context(self, documents: List[Dict]) -> str:
        """
        Format retrieved documents into context string.

        Args:
            documents: List of retrieved documents

        Returns:
            Formatted context string
        """
        context_parts = []
        for i, doc in enumerate(documents, 1):
            part = f"[Document {i}]\n"
            part += f"Section: {doc['section']}\n"
            part += f"Relevance Score: {doc['score']:.4f}\n"
            if doc.get('page_url'):
                part += f"Source: {doc['page_url']}\n"
            part += f"\nContent:\n{doc['content']}\n"
            context_parts.append(part)
        return "\n---\n".join(context_parts)

    def build_prompt(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Build LLM prompt from query and context.

        Args:
            query: User query
            context: Retrieved context
            system_prompt: Custom system prompt

        Returns:
            Complete prompt for LLM
        """
        if system_prompt is None:
            system_prompt = """You are a helpful assistant that answers questions based on provided documentation.

Instructions:
1. Answer ONLY using the provided context
2. If the answer is not in the context, say "I don't have enough information to answer this question"
3. Be concise and clear
4. Cite the relevant sections when appropriate"""

        prompt = f"""{system_prompt}

Context:
{context}

Question:
{query}

Answer:"""

        return prompt

    def generate_answer(
        self,
        query: str,
        documents: List[Dict] = None,
        top_k: int = None,
        system_prompt: Optional[str] = None
    ) -> Dict:
        """
        Generate an answer using RAG pipeline.

        Args:
            query: User query
            documents: Pre-retrieved documents (optional)
            top_k: Number of documents to retrieve
            system_prompt: Custom system prompt

        Returns:
            Dictionary with query, context, and generated answer
        """
        # Retrieve context if not provided
        if documents is None:
            documents = self.retrieve_context(query, top_k=top_k)

        if not documents:
            return {
                "query": query,
                "status": "no_results",
                "message": "No relevant documents found"
            }

        # Format context
        context = self.format_context(documents)

        # Build prompt
        prompt = self.build_prompt(query, context, system_prompt)

        # For now, return the prompt (LLM integration would go here)
        return {
            "query": query,
            "documents": documents,
            "context": context,
            "prompt": prompt,
            "status": "ready_for_llm"
        }

    def close(self) -> None:
        """Close database connection."""
        self.search.close()

    def get_status(self) -> Dict:
        """Get service status."""
        stats = self.search.get_stats()
        return {
            "service": "RAG Service",
            "database": self.db_path,
            "llm_model": self.llm_model,
            "llm_provider": self.llm_provider,
            "stats": stats
        }


class RAGPipeline:
    """Complete RAG pipeline for document Q&A."""

    def __init__(self, db_path: str = None):
        """Initialize RAG pipeline."""
        self.service = RAGService(db_path)

    def process_query(self, query: str, top_k: int = 5) -> Dict:
        """
        Process a query through the complete RAG pipeline.

        Args:
            query: User query
            top_k: Number of documents to retrieve

        Returns:
            Complete pipeline result
        """
        # Retrieve
        documents = self.service.retrieve_context(query, top_k=top_k)

        if not documents:
            return {
                "query": query,
                "status": "no_results"
            }

        # Generate
        result = self.service.generate_answer(query, documents=documents)

        # Add pipeline metadata
        result["pipeline_steps"] = [
            "query_encoding",
            "semantic_search",
            "document_ranking",
            "context_formatting",
            "prompt_building"
        ]

        return result

    def close(self) -> None:
        """Close connections."""
        self.service.close()


# Convenience functions
def rag_answer(query: str, db_path: str = None, top_k: int = 5) -> Dict:
    """Simple RAG interface."""
    rag = RAGPipeline(db_path)
    result = rag.process_query(query, top_k=top_k)
    rag.close()
    return result
