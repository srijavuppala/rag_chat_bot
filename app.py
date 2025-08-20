"""
Streamlit Web Interface for RAG Chatbot
"""
import streamlit as st
import pandas as pd
import time
import logging
from typing import List, Dict, Any
from rag_system import RAGSystem
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="University Course RAG Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #3b82f6;
    }
    .user-message {
        background-color: #eff6ff;
        border-left-color: #3b82f6;
    }
    .bot-message {
        background-color: #f0fdf4;
        border-left-color: #10b981;
    }
    .course-card {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f9fafb;
    }
    .similarity-score {
        background-color: #dbeafe;
        color: #1e40af;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .metrics-container {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_rag_system():
    """Initialize and cache the RAG system"""
    try:
        with st.spinner("Initializing RAG system..."):
            rag_system = RAGSystem()
            return rag_system, None
    except Exception as e:
        error_msg = f"Failed to initialize RAG system: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

def display_course_card(course: Dict[str, Any], show_similarity: bool = True):
    """Display a course information card"""
    with st.container():
        st.markdown(f"""
        <div class="course-card">
            <h4>{course['course_code']} - {course['course_name']}</h4>
            <p><strong>Department:</strong> {course['department']}</p>
            <p><strong>Credits:</strong> {course['credits']}</p>
            <p><strong>Prerequisites:</strong> {course['prerequisites']}</p>
            <p><strong>Description:</strong> {course['description']}</p>
            {f'<span class="similarity-score">Similarity: {course["similarity_score"]:.2f}</span>' if show_similarity and 'similarity_score' in course else ''}
        </div>
        """, unsafe_allow_html=True)

def display_chat_message(message: str, is_user: bool = False):
    """Display a chat message with appropriate styling"""
    css_class = "user-message" if is_user else "bot-message"
    icon = "👤" if is_user else "🤖"
    
    st.markdown(f"""
    <div class="chat-message {css_class}">
        <strong>{icon} {'You' if is_user else 'Assistant'}:</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎓 University Course RAG Chatbot</h1>', unsafe_allow_html=True)
    st.markdown("Ask me anything about university courses! I can help you find courses, understand prerequisites, and make recommendations.")
    
    # Initialize RAG system
    rag_system, error = initialize_rag_system()
    
    if error:
        st.error(f"❌ {error}")
        st.info("💡 Please ensure your database is set up correctly and all dependencies are installed.")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Settings")
        
        # Configuration display
        config = Config()
        st.subheader("Current Configuration")
        st.write(f"**Embedding Model:** {config.EMBEDDING_MODEL}")
        st.write(f"**Max Results:** {config.MAX_RESULTS}")
        st.write(f"**Similarity Threshold:** {config.SIMILARITY_THRESHOLD}")
        
        st.divider()
        
        # Sample queries
        st.subheader("💡 Try These Questions")
        sample_queries = [
            "What programming courses are available?",
            "I want to learn machine learning",
            "What are the prerequisites for AI courses?",
            "Show me data science courses",
            "What courses require CS101?",
            "Tell me about cybersecurity courses"
        ]
        
        for query in sample_queries:
            if st.button(query, key=f"sample_{hash(query)}"):
                st.session_state.user_input = query
        
        st.divider()
        
        # Database status
        st.subheader("📊 System Status")
        if rag_system and rag_system.courses_df is not None:
            st.success(f"✅ {len(rag_system.courses_df)} courses loaded")
            st.success("✅ RAG system ready")
        else:
            st.error("❌ System not ready")
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat Interface")
        
        # User input
        user_input = st.text_input(
            "Ask your question:",
            value=st.session_state.user_input,
            placeholder="e.g., What programming courses should I take first?",
            key="chat_input"
        )
        
        col_send, col_clear = st.columns([1, 1])
        with col_send:
            send_button = st.button("Send 🚀", type="primary", use_container_width=True)
        with col_clear:
            clear_button = st.button("Clear History 🗑️", use_container_width=True)
        
        # Clear chat history
        if clear_button:
            st.session_state.chat_history = []
            st.session_state.user_input = ""
            st.rerun()
        
        # Process user input
        if send_button and user_input.strip():
            with st.spinner("🔍 Searching for relevant courses..."):
                # Add user message to history
                st.session_state.chat_history.append({
                    "type": "user",
                    "message": user_input,
                    "timestamp": time.time()
                })
                
                # Get RAG response
                try:
                    result = rag_system.chat(user_input)
                    
                    # Add bot response to history
                    st.session_state.chat_history.append({
                        "type": "bot",
                        "message": result['response'],
                        "relevant_courses": result['relevant_courses'],
                        "status": result['status'],
                        "timestamp": time.time()
                    })
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.session_state.chat_history.append({
                        "type": "bot",
                        "message": error_msg,
                        "relevant_courses": [],
                        "status": "error",
                        "timestamp": time.time()
                    })
            
            # Clear input and rerun
            st.session_state.user_input = ""
            st.rerun()
        
        # Display chat history
        st.subheader("Chat History")
        chat_container = st.container()
        
        with chat_container:
            if not st.session_state.chat_history:
                st.info("👋 Start by asking a question about university courses!")
            else:
                for chat in reversed(st.session_state.chat_history[-10:]):  # Show last 10 messages
                    display_chat_message(chat['message'], chat['type'] == 'user')
    
    with col2:
        st.header("📚 Course Details")
        
        # Show relevant courses from the last bot response
        if st.session_state.chat_history:
            last_bot_response = None
            for chat in reversed(st.session_state.chat_history):
                if chat['type'] == 'bot':
                    last_bot_response = chat
                    break
            
            if last_bot_response and last_bot_response.get('relevant_courses'):
                st.subheader("📖 Relevant Courses Found")
                
                courses = last_bot_response['relevant_courses']
                
                # Display metrics
                st.markdown(f"""
                <div class="metrics-container">
                    <strong>Search Results:</strong> {len(courses)} courses found<br>
                    <strong>Status:</strong> {last_bot_response['status'].title()}
                </div>
                """, unsafe_allow_html=True)
                
                # Display courses
                for i, course in enumerate(courses):
                    with st.expander(f"{course['course_code']} - {course['course_name']}", expanded=i < 2):
                        display_course_card(course, show_similarity=True)
            else:
                st.info("🔍 Ask a question to see relevant courses here!")
        else:
            st.info("🔍 Ask a question to see relevant courses here!")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.9rem;">
        🤖 Powered by RAG (Retrieval-Augmented Generation) • Built with Streamlit & Sentence Transformers
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()