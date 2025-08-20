"""
RAG (Retrieval-Augmented Generation) System Implementation
"""
import os
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles database operations"""
    
    def __init__(self, database_url: str):
        """Initialize database connection"""
        self.database_url = database_url
        self.engine = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.engine = create_engine(self.database_url)
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def get_all_courses(self) -> pd.DataFrame:
        """Retrieve all courses from database"""
        try:
            query = """
            SELECT id, course_code, course_name, description, 
                   prerequisites, credits, department,
                   course_code || ' - ' || course_name || ': ' || description as full_text
            FROM courses
            ORDER BY course_code
            """
            df = pd.read_sql(query, self.engine)
            logger.info(f"Retrieved {len(df)} courses from database")
            return df
        except SQLAlchemyError as e:
            logger.error(f"Database query failed: {e}")
            raise
    
    def search_courses(self, search_term: str, limit: int = 10) -> pd.DataFrame:
        """Search courses using SQL LIKE query"""
        try:
            query = text("""
            SELECT id, course_code, course_name, description, 
                   prerequisites, credits, department,
                   course_code || ' - ' || course_name || ': ' || description as full_text
            FROM courses 
            WHERE course_code ILIKE :search_term 
               OR course_name ILIKE :search_term 
               OR description ILIKE :search_term
               OR department ILIKE :search_term
            ORDER BY course_code
            LIMIT :limit
            """)
            
            df = pd.read_sql(query, self.engine, params={
                'search_term': f'%{search_term}%',
                'limit': limit
            })
            logger.info(f"Found {len(df)} courses matching '{search_term}'")
            return df
        except SQLAlchemyError as e:
            logger.error(f"Search query failed: {e}")
            raise

class EmbeddingManager:
    """Handles text embeddings for semantic search"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize embedding model"""
        self.model_name = model_name
        self.model = None
        self.embeddings_cache = {}
        self.load_model()
    
    def load_model(self):
        """Load the sentence transformer model"""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """Convert texts to embeddings"""
        try:
            embeddings = self.model.encode(texts, show_progress_bar=True)
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def compute_similarity(self, query_embedding: np.ndarray, 
                          doc_embeddings: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query and document embeddings"""
        # Normalize embeddings
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        doc_norms = doc_embeddings / np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
        
        # Compute cosine similarity
        similarities = np.dot(doc_norms, query_norm)
        return similarities

class LLMManager:
    """Handles Large Language Model operations"""
    
    def __init__(self, model_name: str = "mistralai/Mistral-7B-Instruct-v0.1"):
        """Initialize LLM"""
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.load_model()
    
    def load_model(self):
        """Load the language model"""
        try:
            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            # For demonstration, we'll use a smaller model that's more accessible
            # You can replace this with Mistral when you have proper GPU setup
            model_name = "microsoft/DialoGPT-medium"  # Fallback model
            
            self.pipeline = pipeline(
                "text-generation",
                model=model_name,
                tokenizer=model_name,
                device=0 if device == "cuda" else -1,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32
            )
            
            logger.info(f"Loaded LLM: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load LLM: {e}")
            # Fallback to a simple text generation approach
            self.pipeline = None
    
    def generate_response(self, prompt: str, max_length: int = 512) -> str:
        """Generate response using the LLM"""
        try:
            if self.pipeline is None:
                return self._fallback_response(prompt)
            
            # Generate response
            response = self.pipeline(
                prompt,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.pipeline.tokenizer.eos_token_id
            )
            
            generated_text = response[0]['generated_text']
            # Remove the original prompt from the response
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when LLM is not available"""
        return "I understand you're asking about courses. Based on the retrieved information, I can help you with course details, prerequisites, and recommendations."

class RAGSystem:
    """Main RAG System that combines retrieval and generation"""
    
    def __init__(self, database_url: str = None):
        """Initialize the RAG system"""
        self.config = Config()
        self.db_manager = DatabaseManager(database_url or self.config.get_database_url())
        self.embedding_manager = EmbeddingManager(self.config.EMBEDDING_MODEL)
        self.llm_manager = LLMManager(self.config.LLM_MODEL)
        
        # Cache for course data and embeddings
        self.courses_df = None
        self.course_embeddings = None
        self.load_course_data()
    
    def load_course_data(self):
        """Load and cache course data with embeddings"""
        try:
            self.courses_df = self.db_manager.get_all_courses()
            if not self.courses_df.empty:
                # Generate embeddings for all course descriptions
                course_texts = self.courses_df['full_text'].tolist()
                self.course_embeddings = self.embedding_manager.encode_texts(course_texts)
                logger.info("Course data and embeddings loaded successfully")
            else:
                logger.warning("No courses found in database")
        except Exception as e:
            logger.error(f"Failed to load course data: {e}")
            raise
    
    def retrieve_relevant_courses(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve most relevant courses based on semantic similarity"""
        try:
            if self.courses_df is None or self.course_embeddings is None:
                logger.warning("Course data not loaded, attempting to reload")
                self.load_course_data()
            
            # Generate embedding for the query
            query_embedding = self.embedding_manager.encode_texts([query])[0]
            
            # Compute similarities
            similarities = self.embedding_manager.compute_similarity(
                query_embedding, self.course_embeddings
            )
            
            # Get top-k most similar courses
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            relevant_courses = []
            for idx in top_indices:
                if similarities[idx] >= self.config.SIMILARITY_THRESHOLD:
                    course = self.courses_df.iloc[idx].to_dict()
                    course['similarity_score'] = float(similarities[idx])
                    relevant_courses.append(course)
            
            logger.info(f"Retrieved {len(relevant_courses)} relevant courses for query: {query}")
            return relevant_courses
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []
    
    def generate_response(self, query: str, relevant_courses: List[Dict[str, Any]]) -> str:
        """Generate a response using retrieved courses and LLM"""
        try:
            # Prepare context from retrieved courses
            context = "Here are the relevant courses I found:\n\n"
            for i, course in enumerate(relevant_courses, 1):
                context += f"{i}. {course['course_code']} - {course['course_name']}\n"
                context += f"   Department: {course['department']}\n"
                context += f"   Credits: {course['credits']}\n"
                context += f"   Prerequisites: {course['prerequisites']}\n"
                context += f"   Description: {course['description']}\n"
                context += f"   Relevance Score: {course['similarity_score']:.2f}\n\n"
            
            # Create prompt for LLM
            prompt = f"""
            User Question: {query}
            
            {context}
            
            Based on the above course information, please provide a helpful and informative response to the user's question. 
            Be specific about course details, prerequisites, and make relevant recommendations.
            
            Response:
            """
            
            # Generate response using LLM
            response = self.llm_manager.generate_response(prompt, max_length=512)
            
            return response
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return f"I found {len(relevant_courses)} relevant courses, but encountered an error generating the response. Please try again."
    
    def chat(self, query: str) -> Dict[str, Any]:
        """Main chat interface"""
        try:
            # Retrieve relevant courses
            relevant_courses = self.retrieve_relevant_courses(query, top_k=self.config.MAX_RESULTS)
            
            if not relevant_courses:
                return {
                    "query": query,
                    "response": "I couldn't find any relevant courses for your question. Could you please rephrase or ask about a specific topic?",
                    "relevant_courses": [],
                    "status": "no_results"
                }
            
            # Generate response
            response = self.generate_response(query, relevant_courses)
            
            return {
                "query": query,
                "response": response,
                "relevant_courses": relevant_courses,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return {
                "query": query,
                "response": f"I encountered an error processing your question: {str(e)}",
                "relevant_courses": [],
                "status": "error"
            }

# Example usage
if __name__ == "__main__":
    # Initialize RAG system
    rag = RAGSystem()
    
    # Example queries
    test_queries = [
        "What programming courses are available?",
        "I want to learn about machine learning",
        "What are the prerequisites for advanced AI courses?",
        "Tell me about data science courses"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        
        result = rag.chat(query)
        print(f"Response: {result['response']}")
        print(f"Status: {result['status']}")
        print(f"Found {len(result['relevant_courses'])} relevant courses")