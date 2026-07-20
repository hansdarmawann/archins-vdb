"""
Configuration management for the Archins-rag project.

Loads settings from environment variables and provides default values.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Central configuration class for all project settings."""

    # ============================================
    # Database Configuration
    # ============================================
    DB_PATH = os.getenv("DB_PATH", "../data/linux_docs.db")

    # ============================================
    # Crawler Configuration
    # ============================================
    CRAWLER_TIMEOUT = int(os.getenv("CRAWLER_TIMEOUT", 10))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    USER_AGENT = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    BASE_URL = os.getenv("BASE_URL", "https://wiki.archlinux.org")

    # ============================================
    # Text Processing Configuration
    # ============================================
    MIN_CHUNK_SIZE = int(os.getenv("MIN_CHUNK_SIZE", 200))
    MAX_CHUNK_SIZE = int(os.getenv("MAX_CHUNK_SIZE", 1000))
    OVERLAP_SIZE = int(os.getenv("OVERLAP_SIZE", 100))

    # ============================================
    # Embedding Configuration
    # ============================================
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", 32))
    EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")

    # ============================================
    # Retrieval Configuration
    # ============================================
    SEARCH_TOP_K = int(os.getenv("SEARCH_TOP_K", 5))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.3))

    # ============================================
    # LLM Configuration (Optional)
    # ============================================
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", None)
    LLM_API_KEY = os.getenv("LLM_API_KEY", None)
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 500))

    # ============================================
    # Service Configuration
    # ============================================
    SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8000))
    SERVICE_DEBUG = os.getenv("SERVICE_DEBUG", "False").lower() == "true"

    # ============================================
    # Logging Configuration
    # ============================================
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "./logs/app.log")

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings."""
        errors = []

        # Check database path
        db_dir = Path(cls.DB_PATH).parent
        try:
            db_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create database directory: {e}")

        # Check embedding model device
        if cls.EMBEDDING_DEVICE not in ["cpu", "cuda", "mps"]:
            errors.append(f"Invalid EMBEDDING_DEVICE: {cls.EMBEDDING_DEVICE}")

        # Check chunk sizes
        if cls.MIN_CHUNK_SIZE < 50:
            errors.append("MIN_CHUNK_SIZE should be at least 50")
        if cls.MAX_CHUNK_SIZE < cls.MIN_CHUNK_SIZE:
            errors.append("MAX_CHUNK_SIZE should be >= MIN_CHUNK_SIZE")

        if errors:
            for error in errors:
                print(f"⚠️ Configuration Warning: {error}")
            return False

        return True

    @classmethod
    def display(cls):
        """Display current configuration."""
        print("=" * 50)
        print("CONFIGURATION SETTINGS")
        print("=" * 50)
        
        config_dict = {
            k: v for k, v in vars(cls).items()
            if not k.startswith("_") and isinstance(v, (str, int, float, bool)) or v is None
        }
        
        for key, value in sorted(config_dict.items()):
            if "API_KEY" in key or "PASSWORD" in key:
                value = "***" if value else None
            print(f"  {key}: {value}")
        
        print("=" * 50)
