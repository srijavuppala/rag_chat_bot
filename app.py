import streamlit as st
import time
import uuid
from typing import List, Dict, Optional
from src.rag_pipeline import RAGPipeline
from src.config import Config

# Page configuration
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI with improved readability
st.markdown("""
<style>
/* Main header styling */
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 2rem;
    color: #1f77b4;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

/* Chat message styling with better contrast */
.chat-message {
    padding: 1.2rem;
    border-radius: 0.8rem;
    margin: 0.8rem 0;
    border-left: 4px solid #1f77b4;
    color: #2c3e50;
    font-size: 1.1rem;
    line-height: 1.6;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.user-message {
    background-color: #f8f9fa;
    border-left-color: #e74c3c;
    color: #2c3e50;
    font-weight: 500;
}

.bot-message {
    background-color: #e8f4fd;
    border-left-color: #3498db;
    color: #2c3e50;
}

/* Document stats with better visibility */
.document-stats {
    background-color: #ffffff;
    padding: 1.2rem;
    border-radius: 0.8rem;
    border: 2px solid #3498db;
    color: #2c3e50;
    font-size: 1.1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Follow-up questions with better contrast */
.follow-up-questions {
    background-color: #fff8e1;
    padding: 1.2rem;
    border-radius: 0.8rem;
    border-left: 4px solid #f39c12;
    margin-top: 1rem;
    color: #2c3e50;
    font-size: 1.1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Demo mode banner with better visibility */
.demo-banner {
    background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
    border: 2px solid #e17055;
    border-radius: 0.8rem;
    padding: 1.5rem;
    margin: 1rem 0;
    text-align: center;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.demo-banner h4 {
    margin: 0;
    color: #2c3e50;
    font-size: 1.3rem;
    font-weight: bold;
}

.demo-banner p {
    margin: 0.5rem 0 0 0;
    color: #2c3e50;
    font-size: 1.1rem;
}

/* Improve overall text readability */
.stMarkdown, .stText, .stWrite {
    color: #2c3e50 !important;
    font-size: 1.05rem;
}

/* Sidebar improvements */
.css-1d391kg {
    background-color: #f8f9fa;
}

/* Button styling for better visibility */
.stButton > button {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 0.5rem;
    padding: 0.5rem 1rem;
    font-size: 1rem;
    font-weight: 500;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background-color: #2980b9;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

/* Input field improvements */
.stTextInput > div > div > input {
    font-size: 1.1rem;
    color: #2c3e50;
    background-color: #ffffff;
    border: 2px solid #bdc3c7;
    border-radius: 0.5rem;
    padding: 0.8rem;
}

.stTextInput > div > div > input:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

/* File uploader improvements */
.stFileUploader {
    background-color: #ffffff;
    border: 2px dashed #3498db;
    border-radius: 0.8rem;
    padding: 1rem;
}

/* Expander improvements */
.streamlit-expanderHeader {
    font-size: 1.1rem;
    font-weight: 600;
    color: #2c3e50;
}

/* Text area improvements */
.stTextArea > div > div > textarea {
    background-color: #f8f9fa;
    border: 1px solid #bdc3c7;
    color: #2c3e50;
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state properly
def initialize_session_state():
    """Initialize session state variables"""
    if 'rag_pipeline' not in st.session_state:
        st.session_state.rag_pipeline = None
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'follow_up_questions' not in st.session_state:
        st.session_state.follow_up_questions = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""
    if 'question_counter' not in st.session_state:
        st.session_state.question_counter = 0

# Initialize RAG Pipeline
@st.cache_resource
def initialize_rag_pipeline():
    """Initialize and cache the RAG pipeline"""
    try:
        pipeline = RAGPipeline()
        if pipeline.initialize():
            return pipeline
        else:
            st.error("Failed to initialize RAG pipeline. Please check your configuration.")
            return None
    except Exception as e:
        st.error(f"Error initializing RAG pipeline: {e}")
        return None

def display_chat_message(message: str, is_user: bool = False):
    """Display a chat message with appropriate styling"""
    message_class = "user-message" if is_user else "bot-message"
    role = "👤 User" if is_user else "🤖 Assistant"
    
    # Escape HTML and preserve line breaks
    import html
    escaped_message = html.escape(message).replace('\n', '<br>')
    
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <strong style="font-size: 1.2rem; margin-bottom: 0.5rem; display: inline-block;">{role}:</strong><br>
        <div style="margin-top: 0.5rem; line-height: 1.7;">{escaped_message}</div>
    </div>
    """, unsafe_allow_html=True)

def display_retrieved_documents(documents: List[Dict], section_id: str):
    """Display retrieved documents with unique keys"""
    if not documents:
        return
        
    with st.expander(f"📄 Retrieved Documents ({len(documents)})", expanded=False):
        for i, doc in enumerate(documents):
            filename = doc.get('FILENAME', 'Unknown')
            chunk_text = doc.get('CHUNK_TEXT', '')
            
            st.markdown(f"**Document {i+1}: {filename}**")
            
            # Create truly unique key using section_id, document index, and hash
            doc_hash = hash(chunk_text[:100]) % 10000  # Use first 100 chars for uniqueness
            unique_key = f"doc_{section_id}_{i}_{doc_hash}"
            
            # Display content in a text area
            display_text = chunk_text[:500] + "..." if len(chunk_text) > 500 else chunk_text
            st.text_area(
                f"Content {i+1}",
                value=display_text,
                height=100,
                key=unique_key,
                disabled=True
            )
            
            if i < len(documents) - 1:  # Don't add separator after last document
                st.markdown("---")

def display_follow_up_questions(questions: List[str]):
    """Display follow-up questions as clickable buttons"""
    if not questions:
        return
        
    st.markdown("""
    <div class="follow-up-questions">
        <strong>💡 Suggested follow-up questions:</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Use a counter to ensure unique keys
    if 'followup_counter' not in st.session_state:
        st.session_state.followup_counter = 0
    
    for i, question in enumerate(questions):
        st.session_state.followup_counter += 1
        unique_key = f"followup_{st.session_state.followup_counter}_{i}"
        
        if st.button(f"❓ {question}", key=unique_key):
            # Set the current question and trigger rerun
            st.session_state.current_question = question
            st.session_state.question_counter += 1
            st.rerun()

def render_sidebar():
    """Render the sidebar with controls"""
    with st.sidebar:
        st.header("📊 System Status")
        
        # Health check
        if st.button("🔍 Run Health Check", key="health_check"):
            if st.session_state.rag_pipeline:
                with st.spinner("Checking system health..."):
                    health = st.session_state.rag_pipeline.health_check()
                    
                    for component, status in health.items():
                        icon = "✅" if status else "❌"
                        st.write(f"{icon} {component.replace('_', ' ').title()}: {'OK' if status else 'Error'}")
            else:
                st.error("RAG pipeline not initialized")
        
        st.markdown("---")
        
        # Document upload with enhanced features
        st.header("📁 Upload Documents")
        
        # File format info
        st.info("📋 **Supported formats:** PDF, TXT, CSV, DOCX")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'txt', 'md', 'csv', 'docx'],
            help="Upload documents to add to the knowledge base. Enhanced processing supports PDF, TXT, CSV, and DOCX files",
            key="file_uploader"
        )
        
        # Summarization option
        use_summarization = st.checkbox(
            "🔄 Use AI Summarization",
            value=True,
            help="Summarize document chunks for better retrieval (recommended)",
            key="summarization_checkbox"
        )
        
        if uploaded_file is not None:
            # Show file info
            st.write(f"**File:** {uploaded_file.name}")
            st.write(f"**Type:** {uploaded_file.type}")
            st.write(f"**Size:** {uploaded_file.size:,} bytes")
            
            if st.button("⬆️ Upload & Process", key="upload_btn"):
                if st.session_state.rag_pipeline:
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        success = st.session_state.rag_pipeline.upload_document(
                            uploaded_file, 
                            use_summarization=use_summarization
                        )
                        if success:
                            mode = "with summarization" if use_summarization else "without summarization"
                            st.success(f"✅ Successfully uploaded {uploaded_file.name} ({mode})")
                        else:
                            st.error(f"❌ Failed to upload {uploaded_file.name}")
                else:
                    st.error("RAG pipeline not initialized")
        
        st.markdown("---")
        
        # Document statistics
        st.header("📈 Knowledge Base Stats")
        if st.button("🔄 Refresh Stats", key="refresh_stats"):
            if st.session_state.rag_pipeline:
                stats = st.session_state.rag_pipeline.get_document_statistics()
                
                st.markdown(f"""
                <div class="document-stats">
                    <strong>📚 Total Documents:</strong> {stats['total_documents']}<br>
                    <strong>📝 Total Chunks:</strong> {stats['total_chunks']}<br>
                </div>
                """, unsafe_allow_html=True)
                
                if stats['recent_documents']:
                    st.write("**Recent Documents:**")
                    for doc in stats['recent_documents'][:3]:
                        st.write(f"• {doc['FILENAME']}")
            else:
                st.error("RAG pipeline not initialized")
        
        st.markdown("---")
        
        # Chat controls
        st.header("💬 Chat Controls")
        if st.button("🗑️ Clear Chat History", key="clear_chat"):
            if st.session_state.rag_pipeline:
                st.session_state.rag_pipeline.clear_chat_history()
            st.session_state.chat_history = []
            st.session_state.follow_up_questions = []
            st.session_state.current_question = ""
            st.success("Chat history cleared!")
            st.rerun()

def render_chat_interface():
    """Render the main chat interface"""
    st.header("💬 Ask Questions About Your Documents")
    
    # Display chat history
    if st.session_state.chat_history:
        st.subheader("Chat History")
        for idx, chat in enumerate(st.session_state.chat_history):
            display_chat_message(chat['question'], is_user=True)
            display_chat_message(chat['response'], is_user=False)
            
            if chat.get('retrieved_docs'):
                display_retrieved_documents(chat['retrieved_docs'], f"history_{idx}")
    
    # Question input with proper session state handling
    question_value = st.session_state.current_question if st.session_state.current_question else ""
    
    user_question = st.text_input(
        "Ask a question:",
        value=question_value,
        placeholder="What would you like to know about your documents?",
        key=f"user_question_{st.session_state.question_counter}"
    )
    
    # Clear current question after setting it
    if st.session_state.current_question:
        st.session_state.current_question = ""
    
    col1, col2 = st.columns([1, 4])
    with col1:
        ask_button = st.button("🚀 Ask", type="primary", key="ask_btn")
    
    # Process question
    if ask_button and user_question and st.session_state.rag_pipeline:
        with st.spinner("Thinking..."):
            try:
                # Process the question
                response, retrieved_docs, follow_up_questions = st.session_state.rag_pipeline.process_question(
                    user_question=user_question,
                    include_history=True
                )
                
                # Add to chat history
                st.session_state.chat_history.append({
                    'question': user_question,
                    'response': response,
                    'retrieved_docs': retrieved_docs
                })
                
                # Store follow-up questions
                st.session_state.follow_up_questions = follow_up_questions
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error processing question: {e}")
    
    # Display current response
    if st.session_state.chat_history:
        latest_chat = st.session_state.chat_history[-1]
        
        st.markdown("### 💬 Latest Response")
        display_chat_message(latest_chat['question'], is_user=True)
        display_chat_message(latest_chat['response'], is_user=False)
        
        # Show retrieved documents
        if latest_chat.get('retrieved_docs'):
            display_retrieved_documents(latest_chat['retrieved_docs'], "latest")
        
        # Show follow-up questions
        if st.session_state.follow_up_questions:
            display_follow_up_questions(st.session_state.follow_up_questions)

def main():
    """Main application function"""
    # Initialize session state first
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 RAG Chatbot</h1>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #666;'>{Config.APP_DESCRIPTION}</p>", 
                unsafe_allow_html=True)
    
    # Demo mode banner
    if Config.DEMO_MODE:
        st.markdown("""
        <div class='demo-banner'>
            <h4>🎭 DEMO MODE ACTIVE</h4>
            <p>
                You're exploring the interface with mock data. Add real credentials to .env file for full functionality.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize pipeline
    if not st.session_state.initialized:
        with st.spinner("Initializing RAG pipeline..."):
            st.session_state.rag_pipeline = initialize_rag_pipeline()
            if st.session_state.rag_pipeline:
                st.session_state.initialized = True
                # Check if we're in demo mode
                if Config.DEMO_MODE or not st.session_state.rag_pipeline._has_real_credentials():
                    st.success("🎭 RAG pipeline initialized in DEMO MODE!")
                    st.info("💡 Update your .env file with real Snowflake and Mistral credentials to enable full functionality")
                else:
                    st.success("✅ RAG pipeline initialized successfully!")
            else:
                st.error("❌ Failed to initialize RAG pipeline")
                st.stop()
    
    # Render sidebar
    render_sidebar()
    
    # Render main chat interface
    render_chat_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        Powered by Snowflake Cortex Search 🔍 | Mistral LLM 🧠 | Streamlit ⚡
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 