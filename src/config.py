import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for RAG Chatbot application"""
    
    # Snowflake Configuration
    SNOWFLAKE_ACCOUNT: str = os.getenv("SNOWFLAKE_ACCOUNT", "")
    SNOWFLAKE_USER: str = os.getenv("SNOWFLAKE_USER", "")
    SNOWFLAKE_PASSWORD: str = os.getenv("SNOWFLAKE_PASSWORD", "")
    SNOWFLAKE_WAREHOUSE: str = os.getenv("SNOWFLAKE_WAREHOUSE", "")
    SNOWFLAKE_DATABASE: str = os.getenv("SNOWFLAKE_DATABASE", "RAG_CHATBOT_DB")
    SNOWFLAKE_SCHEMA: str = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
    SNOWFLAKE_ROLE: str = os.getenv("SNOWFLAKE_ROLE", "")
    
    # Mistral Configuration
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    
    # Application Configuration
    APP_TITLE: str = os.getenv("APP_TITLE", "RAG Chatbot")
    APP_DESCRIPTION: str = os.getenv("APP_DESCRIPTION", "AI-powered document Q&A system")
    
    # Demo Mode Configuration
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    
    # RAG Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    MAX_RETRIEVED_DOCS: int = int(os.getenv("MAX_RETRIEVED_DOCS", "5"))
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present"""
        required_fields = [
            cls.SNOWFLAKE_ACCOUNT,
            cls.SNOWFLAKE_USER,
            cls.SNOWFLAKE_PASSWORD,
            cls.SNOWFLAKE_WAREHOUSE,
            cls.MISTRAL_API_KEY
        ]
        
        missing_fields = [field for field in required_fields if not field]
        
        if missing_fields:
            print(f"Missing required configuration fields: {len(missing_fields)} fields")
            return False
        
        return True
    
    @classmethod
    def get_snowflake_connection_params(cls) -> dict:
        """Get Snowflake connection parameters"""
        params = {
            "account": cls.SNOWFLAKE_ACCOUNT,
            "user": cls.SNOWFLAKE_USER,
            "password": cls.SNOWFLAKE_PASSWORD,
            "warehouse": cls.SNOWFLAKE_WAREHOUSE,
            "database": cls.SNOWFLAKE_DATABASE,
            "schema": cls.SNOWFLAKE_SCHEMA
        }
        
        # Add role if specified
        if cls.SNOWFLAKE_ROLE:
            params["role"] = cls.SNOWFLAKE_ROLE
            
        return params 