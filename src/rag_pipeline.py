import uuid
from typing import List, Dict, Optional, Tuple
from src.snowflake_client import SnowflakeClient
from src.mistral_client import MistralClient
from src.enhanced_document_processor import EnhancedDocumentProcessor
from src.config import Config

class RAGPipeline:
    """Main RAG pipeline combining retrieval and generation"""
    
    def __init__(self):
        self.snowflake_client = SnowflakeClient()
        self.mistral_client = MistralClient()
        self.document_processor = EnhancedDocumentProcessor(self.snowflake_client)
        self.session_id = str(uuid.uuid4())
    
    def initialize(self) -> bool:
        """Initialize the RAG pipeline and establish connections"""
        try:
            # Check if we're in demo mode with placeholder credentials
            if Config.DEMO_MODE or not self._has_real_credentials():
                print("🎭 Running in DEMO MODE - Snowflake connection skipped")
                print("📝 To use full functionality, update your .env file with real credentials")
                return True
            
            # Connect to Snowflake
            if not self.snowflake_client.connect():
                print("Failed to connect to Snowflake")
                print("💡 Try setting DEMO_MODE=true in .env to explore the interface")
                return False
            
            # Validate configuration
            if not Config.validate_config():
                print("Configuration validation failed")
                return False
            
            print("RAG Pipeline initialized successfully")
            return True
            
        except Exception as e:
            print(f"Failed to initialize RAG pipeline: {e}")
            return False
    
    def _has_real_credentials(self) -> bool:
        """Check if we have real credentials (not placeholders)"""
        placeholder_indicators = [
            "your_account_name",
            "your_username", 
            "your_password",
            "your_warehouse",
            "your_mistral_api_key"
        ]
        
        credentials = [
            Config.SNOWFLAKE_ACCOUNT,
            Config.SNOWFLAKE_USER,
            Config.SNOWFLAKE_PASSWORD,
            Config.SNOWFLAKE_WAREHOUSE,
            Config.MISTRAL_API_KEY
        ]
        
        for cred in credentials:
            if any(placeholder in cred.lower() for placeholder in placeholder_indicators):
                return False
        
        return all(credentials)  # All credentials must be non-empty
    
    def process_question(self, 
                        user_question: str, 
                        include_history: bool = True) -> Tuple[str, List[Dict], List[str]]:
        """
        Process a user question through the complete RAG pipeline
        
        Returns:
            Tuple of (response, retrieved_documents, follow_up_questions)
        """
        try:
            # Handle demo mode
            if Config.DEMO_MODE or not self._has_real_credentials():
                return self._demo_process_question(user_question)
            
            # Step 1: Retrieve relevant documents using Cortex Search
            retrieved_docs = self._retrieve_documents(user_question)
            
            # Step 2: Get chat history if requested
            chat_history = []
            if include_history:
                chat_history = self.snowflake_client.get_chat_history(
                    self.session_id, 
                    limit=5
                )
            
            # Step 3: Generate response using Mistral LLM
            response = self.mistral_client.generate_response(
                user_question=user_question,
                context_documents=retrieved_docs,
                chat_history=chat_history
            )
            
            # Step 4: Generate follow-up questions
            follow_up_questions = self.mistral_client.generate_follow_up_questions(
                user_question=user_question,
                bot_response=response,
                context_documents=retrieved_docs
            )
            
            # Step 5: Save interaction to chat history
            self.snowflake_client.save_chat_history(
                session_id=self.session_id,
                question=user_question,
                response=response,
                retrieved_docs=retrieved_docs
            )
            
            return response, retrieved_docs, follow_up_questions
            
        except Exception as e:
            error_msg = f"Error processing question: {e}"
            print(error_msg)
            return error_msg, [], []
    
    def _demo_process_question(self, user_question: str) -> Tuple[str, List[Dict], List[str]]:
        """Handle questions in demo mode with mock responses"""
        
        # Mock retrieved documents
        demo_docs = [
            {
                'CHUNK_TEXT': f"This is a demo document chunk related to your question: '{user_question}'. In a real deployment, this would be content from your uploaded documents that's most relevant to your query.",
                'FILENAME': 'demo_document.pdf',
                'CHUNK_METADATA': '{"chunk_index": 0, "demo": true}',
                'DOC_METADATA': '{"demo": true}'
            },
            {
                'CHUNK_TEXT': "This is another demo chunk showing how multiple relevant sections from your documents would be retrieved and used to generate comprehensive answers.",
                'FILENAME': 'sample_guide.txt',
                'CHUNK_METADATA': '{"chunk_index": 1, "demo": true}',
                'DOC_METADATA': '{"demo": true}'
            }
        ]
        
        # Mock response
        response = f"""🎭 **DEMO MODE RESPONSE**

Thank you for asking: "{user_question}"

In full mode with your Snowflake and Mistral credentials configured, I would:

1. **🔍 Search** your uploaded documents using Snowflake Cortex Search
2. **📄 Retrieve** the most relevant document chunks 
3. **🧠 Generate** a comprehensive answer using Mistral LLM
4. **💾 Save** our conversation to chat history

**To enable full functionality:**
- Add your Snowflake credentials to the `.env` file
- Add your Mistral API key
- Upload documents and ask real questions!

This demo shows you the interface and features available."""
        
        # Mock follow-up questions
        follow_up_questions = [
            "How do I configure my Snowflake credentials?",
            "What document formats are supported?",
            "How does the RAG pipeline work?"
        ]
        
        return response, demo_docs, follow_up_questions
    
    def _retrieve_documents(self, query: str) -> List[Dict]:
        """Retrieve relevant documents using Snowflake Cortex Search"""
        try:
            # Use Cortex Search to find relevant document chunks
            results = self.snowflake_client.search_documents_cortex(
                query=query,
                limit=Config.MAX_RETRIEVED_DOCS
            )
            
            if not results:
                print(f"No documents found for query: {query}")
            else:
                print(f"Retrieved {len(results)} relevant documents")
            
            return results
            
        except Exception as e:
            print(f"Document retrieval failed: {e}")
            return []
    
    def upload_document(self, uploaded_file, metadata: Dict = None, use_summarization: bool = True) -> bool:
        """Upload and process a new document with enhanced features"""
        try:
            # Handle demo mode
            if Config.DEMO_MODE or not self._has_real_credentials():
                print(f"🎭 DEMO MODE: Simulated upload of '{uploaded_file.name}'")
                print("📝 In full mode, this would be processed and stored in Snowflake")
                return True
            
            success = self.document_processor.ingest_document_enhanced(
                uploaded_file=uploaded_file,
                metadata=metadata,
                use_summarization=use_summarization
            )
            
            if success:
                print(f"Document '{uploaded_file.name}' uploaded and processed successfully")
            else:
                print(f"Failed to upload document '{uploaded_file.name}'")
            
            return success
            
        except Exception as e:
            print(f"Document upload failed: {e}")
            return False
    
    def get_document_statistics(self) -> Dict:
        """Get statistics about the document collection"""
        if Config.DEMO_MODE or not self._has_real_credentials():
            return {
                "total_documents": 3,
                "total_chunks": 15,
                "recent_documents": [
                    {"FILENAME": "demo_document.pdf"},
                    {"FILENAME": "sample_guide.txt"}, 
                    {"FILENAME": "example_manual.md"}
                ]
            }
        return self.document_processor.get_document_stats()
    
    def get_chat_history(self, limit: int = 10) -> List[Dict]:
        """Get chat history for current session"""
        return self.snowflake_client.get_chat_history(self.session_id, limit)
    
    def clear_chat_history(self) -> bool:
        """Clear chat history and start new session"""
        try:
            self.session_id = str(uuid.uuid4())
            print("Chat history cleared, new session started")
            return True
        except Exception as e:
            print(f"Failed to clear chat history: {e}")
            return False
    
    def search_documents(self, query: str, limit: int = 10) -> List[Dict]:
        """Search documents directly (for exploration/debugging)"""
        return self.snowflake_client.search_documents_cortex(query, limit)
    
    def generate_document_summary(self, document_text: str) -> str:
        """Generate a summary of a document"""
        return self.mistral_client.generate_summary(document_text)
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all pipeline components"""
        health_status = {
            "snowflake_connection": False,
            "mistral_api": False,
            "configuration": False
        }
        
        try:
            # Handle demo mode
            if Config.DEMO_MODE or not self._has_real_credentials():
                health_status = {
                    "demo_mode": True,
                    "interface": True,
                    "configuration": False
                }
                return health_status
            
            # Check Snowflake connection
            test_query = "SELECT 1 as test"
            result = self.snowflake_client.execute_query(test_query)
            health_status["snowflake_connection"] = result is not None
            
            # Check Mistral API (simple test)
            test_response = self.mistral_client.generate_response(
                user_question="Test",
                context_documents=[],
                chat_history=[]
            )
            health_status["mistral_api"] = bool(test_response and "trouble" not in test_response.lower())
            
            # Check configuration
            health_status["configuration"] = Config.validate_config()
            
        except Exception as e:
            print(f"Health check failed: {e}")
        
        return health_status
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.snowflake_client:
                self.snowflake_client.disconnect()
            print("RAG Pipeline cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}") 