#!/usr/bin/env python3
"""
Simple test of RAG system without external dependencies
"""
import json
from typing import List, Dict, Any

class SimpleRAGTest:
    """Simple RAG system test using basic Python only"""
    
    def __init__(self):
        """Initialize with sample data"""
        self.courses = [
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
    
    def search_courses(self, query: str) -> List[Dict[str, Any]]:
        """Simple keyword-based search"""
        query_lower = query.lower()
        results = []
        
        for course in self.courses:
            score = 0
            searchable_text = (
                course['course_code'] + ' ' + 
                course['course_name'] + ' ' + 
                course['description'] + ' ' + 
                course['department']
            ).lower()
            
            # Count keyword matches
            for word in query_lower.split():
                if word in searchable_text:
                    score += searchable_text.count(word)
            
            if score > 0:
                course_copy = course.copy()
                course_copy['relevance_score'] = score
                results.append(course_copy)
        
        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:5]  # Return top 5
    
    def generate_response(self, query: str, courses: List[Dict[str, Any]]) -> str:
        """Generate a simple response"""
        if not courses:
            return f"No courses found matching '{query}'. Try different keywords."
        
        response = f"Found {len(courses)} course(s) related to '{query}':\n\n"
        
        for i, course in enumerate(courses, 1):
            response += f"{i}. {course['course_code']} - {course['course_name']}\n"
            response += f"   Department: {course['department']}\n"
            response += f"   Credits: {course['credits']}\n"
            response += f"   Prerequisites: {course['prerequisites']}\n"
            response += f"   Description: {course['description']}\n"
            response += f"   Relevance: {course['relevance_score']} matches\n\n"
        
        return response
    
    def chat(self, query: str) -> Dict[str, Any]:
        """Main chat function"""
        courses = self.search_courses(query)
        response = self.generate_response(query, courses)
        
        return {
            'query': query,
            'response': response,
            'courses_found': len(courses),
            'courses': courses
        }

def main():
    """Test the simple RAG system"""
    print("🎓 Simple RAG Chatbot Test")
    print("=" * 50)
    
    rag = SimpleRAGTest()
    
    # Test queries
    test_queries = [
        "programming courses",
        "machine learning",
        "web development",
        "data science",
        "artificial intelligence",
        "prerequisites for CS102"
    ]
    
    print("🤖 Testing with sample queries:\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}: {query}")
        print("-" * 30)
        
        result = rag.chat(query)
        print(f"Courses found: {result['courses_found']}")
        print(f"Response:\n{result['response']}")
        print("=" * 50)
    
    # Interactive test
    print("💬 Interactive mode (type 'quit' to exit):")
    while True:
        user_query = input("\nYour question: ").strip()
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if user_query:
            result = rag.chat(user_query)
            print(f"\n🤖 {result['response']}")

def test_project_structure():
    """Test that all project files are present"""
    import os
    
    required_files = [
        'README.md',
        'requirements.txt',
        'config.py',
        'rag_system.py',
        'app.py',
        'demo_offline.py',
        'database_setup.sql',
        '.env.example',
        'Dockerfile',
        'docker-compose.yml',
        'setup.py'
    ]
    
    print("📁 Checking project structure:")
    print("-" * 30)
    
    all_present = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_present = False
    
    print("-" * 30)
    if all_present:
        print("✅ All required files are present!")
    else:
        print("❌ Some files are missing!")
    
    return all_present

if __name__ == "__main__":
    print("🔍 Testing project structure first...\n")
    structure_ok = test_project_structure()
    
    if structure_ok:
        print("\n" + "=" * 50)
        main()
    else:
        print("\n❌ Project structure incomplete. Please ensure all files are created.")