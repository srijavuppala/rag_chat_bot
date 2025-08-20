"""
Offline Demo of RAG System (without database dependency)
This demo uses in-memory data to showcase the RAG functionality
"""
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OfflineRAGDemo:
    """Simplified RAG system for demonstration without database dependency"""
    
    def __init__(self):
        """Initialize with sample data"""
        self.courses_data = self._create_sample_data()
        self.embedding_model = None
        self.course_embeddings = None
        self.load_embedding_model()
        self.generate_embeddings()
    
    def _create_sample_data(self) -> pd.DataFrame:
        """Create sample course data"""
        courses = [
            {
                'id': 1, 'course_code': 'CS101', 'course_name': 'Introduction to Programming',
                'description': 'Learn the fundamentals of programming using Python. Covers variables, loops, functions, and basic data structures.',
                'prerequisites': 'None', 'credits': 3, 'department': 'Computer Science'
            },
            {
                'id': 2, 'course_code': 'CS102', 'course_name': 'Data Structures',
                'description': 'Study of fundamental data structures including arrays, linked lists, stacks, queues, trees, and graphs.',
                'prerequisites': 'CS101', 'credits': 4, 'department': 'Computer Science'
            },
            {
                'id': 3, 'course_code': 'DS202', 'course_name': 'Data Science Fundamentals',
                'description': 'An introduction to data analysis, visualization, and machine learning using Python and R.',
                'prerequisites': 'CS101, MATH201', 'credits': 4, 'department': 'Data Science'
            },
            {
                'id': 4, 'course_code': 'AI404', 'course_name': 'Advanced Natural Language Processing',
                'description': 'Deep dive into modern NLP techniques including transformers, BERT, and GPT models.',
                'prerequisites': 'DS301, CS201', 'credits': 4, 'department': 'Artificial Intelligence'
            },
            {
                'id': 5, 'course_code': 'WEB201', 'course_name': 'Web Development',
                'description': 'Full-stack web development using HTML, CSS, JavaScript, and modern frameworks like React.',
                'prerequisites': 'CS101', 'credits': 3, 'department': 'Computer Science'
            },
            {
                'id': 6, 'course_code': 'ML301', 'course_name': 'Machine Learning',
                'description': 'Comprehensive study of machine learning algorithms including supervised and unsupervised learning, neural networks.',
                'prerequisites': 'DS202, MATH202', 'credits': 4, 'department': 'Data Science'
            }
        ]
        
        df = pd.DataFrame(courses)
        df['full_text'] = df['course_code'] + ' - ' + df['course_name'] + ': ' + df['description']
        return df
    
    def load_embedding_model(self):
        """Load a lightweight embedding model"""
        try:
            # Use a smaller, faster model for demo
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            # Fallback to simple keyword matching
            self.embedding_model = None
    
    def generate_embeddings(self):
        """Generate embeddings for all courses"""
        if self.embedding_model:
            try:
                course_texts = self.courses_data['full_text'].tolist()
                self.course_embeddings = self.embedding_model.encode(course_texts)
                logger.info("Course embeddings generated")
            except Exception as e:
                logger.error(f"Failed to generate embeddings: {e}")
                self.course_embeddings = None
    
    def retrieve_relevant_courses(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant courses using semantic similarity"""
        if self.embedding_model is None or self.course_embeddings is None:
            return self._fallback_keyword_search(query, top_k)
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Compute similarities
            similarities = np.dot(self.course_embeddings, query_embedding.T).flatten()
            similarities = similarities / (np.linalg.norm(self.course_embeddings, axis=1) * np.linalg.norm(query_embedding))
            
            # Get top-k courses
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            relevant_courses = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Threshold for relevance
                    course = self.courses_data.iloc[idx].to_dict()
                    course['similarity_score'] = float(similarities[idx])
                    relevant_courses.append(course)
            
            return relevant_courses
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return self._fallback_keyword_search(query, top_k)
    
    def _fallback_keyword_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Fallback keyword-based search"""
        query_lower = query.lower()
        relevant_courses = []
        
        for _, course in self.courses_data.iterrows():
            score = 0
            full_text = course['full_text'].lower()
            
            # Simple keyword matching
            for word in query_lower.split():
                if word in full_text:
                    score += 1
            
            if score > 0:
                course_dict = course.to_dict()
                course_dict['similarity_score'] = score / len(query_lower.split())
                relevant_courses.append(course_dict)
        
        # Sort by score and return top-k
        relevant_courses.sort(key=lambda x: x['similarity_score'], reverse=True)
        return relevant_courses[:top_k]
    
    def generate_response(self, query: str, relevant_courses: List[Dict[str, Any]]) -> str:
        """Generate a simple response based on retrieved courses"""
        if not relevant_courses:
            return "I couldn't find any relevant courses for your query. Please try a different search term."
        
        response = f"Based on your question '{query}', I found {len(relevant_courses)} relevant course(s):\n\n"
        
        for i, course in enumerate(relevant_courses, 1):
            response += f"{i}. **{course['course_code']} - {course['course_name']}**\n"
            response += f"   - Department: {course['department']}\n"
            response += f"   - Credits: {course['credits']}\n"
            response += f"   - Prerequisites: {course['prerequisites']}\n"
            response += f"   - Description: {course['description']}\n"
            response += f"   - Relevance Score: {course['similarity_score']:.2f}\n\n"
        
        # Add some recommendations
        if "programming" in query.lower() or "coding" in query.lower():
            response += "💡 **Recommendation:** Start with CS101 if you're new to programming, then progress to CS102 for data structures.\n"
        elif "machine learning" in query.lower() or "ai" in query.lower():
            response += "💡 **Recommendation:** Build a strong foundation with DS202 before taking advanced ML courses like ML301 or AI404.\n"
        elif "web" in query.lower():
            response += "💡 **Recommendation:** Make sure you have basic programming knowledge (CS101) before starting web development.\n"
        
        return response
    
    def chat(self, query: str) -> Dict[str, Any]:
        """Main chat interface"""
        try:
            relevant_courses = self.retrieve_relevant_courses(query)
            response = self.generate_response(query, relevant_courses)
            
            return {
                "query": query,
                "response": response,
                "relevant_courses": relevant_courses,
                "status": "success" if relevant_courses else "no_results"
            }
        except Exception as e:
            return {
                "query": query,
                "response": f"An error occurred: {str(e)}",
                "relevant_courses": [],
                "status": "error"
            }

def main():
    """Demo the RAG system"""
    print("🎓 University Course RAG Chatbot Demo")
    print("=" * 50)
    
    # Initialize the demo system
    try:
        rag_demo = OfflineRAGDemo()
        print("✅ RAG system initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        return
    
    # Sample queries
    test_queries = [
        "What programming courses are available?",
        "I want to learn machine learning",
        "Show me web development courses",
        "What are advanced AI courses?",
        "Tell me about data science"
    ]
    
    print("\n🤖 Let me answer some sample questions:\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. Query: {query}")
        print("-" * 40)
        
        result = rag_demo.chat(query)
        print(f"Status: {result['status']}")
        print(f"Response:\n{result['response']}")
        print("=" * 50)
    
    # Interactive mode
    print("\n💬 Interactive Mode (type 'quit' to exit):")
    while True:
        user_query = input("\nYour question: ").strip()
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if user_query:
            result = rag_demo.chat(user_query)
            print(f"\n🤖 Response:\n{result['response']}")

if __name__ == "__main__":
    main()