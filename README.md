# 🎓 University Course RAG Chatbot

A sophisticated **Retrieval-Augmented Generation (RAG)** chatbot that helps students discover and learn about university courses through natural language queries. Built with modern AI technologies including semantic search and large language models.

## ✨ Features

### 🔍 **Intelligent Course Discovery**
- **Semantic Search**: Uses sentence transformers (all-MiniLM-L6-v2) for meaning-based course matching
- **Natural Language Queries**: Ask questions like "What programming courses should I take first?"
- **Contextual Understanding**: Goes beyond keyword matching to understand intent

### 🤖 **AI-Powered Responses**
- **LLM Integration**: Powered by Mistral for natural, helpful responses
- **Personalized Recommendations**: Tailored course suggestions based on interests and prerequisites
- **Academic Pathway Guidance**: Understand course sequences and dependencies

### 💾 **Robust Data Management**
- **PostgreSQL Backend**: Scalable database for course information
- **Comprehensive Course Data**: Detailed information including prerequisites, credits, descriptions
- **Optimized Queries**: Indexed database for fast retrieval

### 🌐 **Modern Web Interface**
- **Streamlit UI**: Clean, interactive web application
- **Real-time Chat**: Instant responses with course details
- **Responsive Design**: Works on desktop and mobile devices
- **Visual Course Cards**: Rich display of course information with similarity scores

## 🚀 Quick Start

### Option 1: Simple Demo (No Setup Required)
```bash
python3 simple_test.py
```

### Option 2: Interactive Demo Runner
```bash
python3 run_demo.py
```

### Option 3: Full Web Application
```bash
# With Docker (Recommended)
docker-compose up

# Or manually
pip install -r requirements.txt
streamlit run app.py
```

## 📁 Project Structure

```
rag-chatbot/
├── 🌐 app.py                 # Main Streamlit web application
├── 🧠 rag_system.py         # Core RAG implementation
├── ⚙️  config.py             # Configuration management
├── 🎮 demo_offline.py       # Offline demo (no database)
├── 🧪 simple_test.py        # Basic functionality test
├── 🎯 run_demo.py           # Interactive demo launcher
├── 📊 database_setup.sql    # Database schema & sample data
├── 📋 requirements.txt      # Python dependencies
├── 🔧 .env.example         # Environment template
├── 🐳 Dockerfile           # Container configuration
├── 🐙 docker-compose.yml   # Multi-service setup
├── 📦 setup.py            # Package configuration
├── 📖 SETUP_GUIDE.md      # Detailed setup instructions
├── ✉️  PROFESSIONAL_EMAIL.md # Email template for professors
└── 📚 README.md           # This file
```

## 🛠️ Technology Stack

### **Backend & AI**
- **Python 3.8+** - Core language
- **Sentence Transformers** - Semantic embeddings
- **Transformers/Mistral** - Large language model
- **PyTorch** - ML framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Database

### **Frontend & UI**
- **Streamlit** - Web framework
- **HTML/CSS** - Custom styling
- **Pandas** - Data manipulation

### **DevOps & Deployment**
- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration
- **Environment Management** - Configuration handling

## 💡 Sample Queries

Try asking these questions:
- "What programming courses are available?"
- "I want to learn machine learning - what should I take?"
- "What are the prerequisites for advanced AI courses?"
- "Show me data science courses for beginners"
- "What courses require CS101 as a prerequisite?"
- "Tell me about cybersecurity courses"

## 🎯 Use Cases

### **For Students**
- **Course Discovery**: Find relevant courses based on interests
- **Academic Planning**: Understand course sequences and prerequisites
- **24/7 Availability**: Get course information anytime

### **For Advisors**
- **Reduced Workload**: Handle routine course inquiries automatically
- **Consistent Information**: Provide standardized course details
- **Analytics**: Track common student questions and interests

### **For Institutions**
- **Improved Accessibility**: Make course information more discoverable
- **Enhanced User Experience**: Modern, intuitive interface
- **Scalability**: Handle large course catalogs efficiently

## 📈 Technical Highlights

- **RAG Architecture**: Combines retrieval and generation for accurate responses
- **Vector Similarity**: Uses cosine similarity for semantic matching
- **Caching**: Optimized performance with embedding caching
- **Error Handling**: Robust error management and fallback mechanisms
- **Modular Design**: Clean separation of concerns for maintainability
- **Docker Support**: Easy deployment and scaling

## 🔧 Configuration

See `SETUP_GUIDE.md` for detailed setup instructions, including:
- Environment setup
- Database configuration
- Docker deployment
- Troubleshooting guide

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

This project is open source under the MIT License. See LICENSE file for details.

## 🎓 Academic Use

This project is designed to be educational and can serve as:
- **Learning Resource**: Understand RAG systems and modern AI
- **Research Foundation**: Basis for academic research projects
- **Portfolio Piece**: Demonstrate technical skills to professors/employers
- **Teaching Tool**: Use in AI/ML courses and workshops

For academic presentations, see `PROFESSIONAL_EMAIL.md` for a template email to professors.

---

**Built with ❤️ for the AI and Education communities**

*This project demonstrates the practical application of RAG systems in educational technology, combining semantic search, large language models, and modern web development to create an intelligent course discovery system.*