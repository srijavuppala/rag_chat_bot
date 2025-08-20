"""
Configuration settings for the RAG Chatbot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for RAG Chatbot"""
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://username:password@localhost:5432/rag_chatbot')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'rag_chatbot')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    
    # Model Configuration
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    LLM_MODEL = os.getenv('LLM_MODEL', 'mistralai/Mistral-7B-Instruct-v0.1')
    
    # Application Settings
    MAX_RESULTS = int(os.getenv('MAX_RESULTS', '5'))
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.3'))
    
    # Hugging Face Token (optional)
    HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
    
    @classmethod
    def get_database_url(cls):
        """Construct database URL from individual components"""
        if cls.DATABASE_URL and cls.DATABASE_URL != 'postgresql://username:password@localhost:5432/rag_chatbot':
            return cls.DATABASE_URL
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"