# RAG Chatbot Setup Guide 🎓

This guide will help you set up and run the RAG (Retrieval-Augmented Generation) chatbot for university courses.

## Quick Start Options

### Option 1: Simple Demo (No Dependencies Required)
```bash
python3 simple_test.py
```
This runs a basic version using only Python standard library.

### Option 2: Full Demo (Requires Dependencies)
```bash
python3 run_demo.py
```
This script will guide you through running either the offline demo or the full web app.

### Option 3: Docker Setup (Recommended for Production)
```bash
docker-compose up -d
```
This sets up PostgreSQL database and runs the full application.

## Detailed Setup Instructions

### 1. Environment Setup

#### Create Virtual Environment
```bash
python3 -m venv rag_chatbot_env
source rag_chatbot_env/bin/activate  # On Windows: rag_chatbot_env\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup

#### Option A: Using Docker (Easiest)
```bash
docker-compose up postgres -d
```

#### Option B: Local PostgreSQL
1. Install PostgreSQL
2. Create database:
```sql
CREATE DATABASE rag_chatbot;
```
3. Run setup script:
```bash
psql -U your_username -d rag_chatbot -f database_setup.sql
```

### 3. Configuration

#### Copy Environment File
```bash
cp .env.example .env
```

#### Edit Configuration
Update `.env` with your database credentials:
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/rag_chatbot
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag_chatbot
DB_USER=your_username
DB_PASSWORD=your_password
```

### 4. Run the Application

#### Streamlit Web App
```bash
streamlit run app.py
```
Access at: http://localhost:8501

#### Offline Demo
```bash
python3 demo_offline.py
```

#### Interactive Demo Runner
```bash
python3 run_demo.py
```

## Features

### 🔍 Semantic Search
- Uses sentence transformers for semantic similarity
- Finds relevant courses based on meaning, not just keywords

### 🤖 LLM Integration
- Integrates with Mistral or compatible models
- Generates natural language responses

### 💾 Database Backend
- PostgreSQL for scalable data storage
- Comprehensive course information

### 🌐 Web Interface
- Clean, modern Streamlit UI
- Interactive chat interface
- Course details display

## Project Structure

```
rag-chatbot/
├── app.py                 # Main Streamlit web application
├── rag_system.py         # Core RAG implementation
├── config.py             # Configuration settings
├── demo_offline.py       # Offline demo without database
├── simple_test.py        # Basic test without dependencies
├── run_demo.py           # Interactive demo runner
├── database_setup.sql    # Database schema and sample data
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── Dockerfile           # Docker container configuration
├── docker-compose.yml   # Multi-container setup
├── setup.py            # Package setup
└── README.md           # Project documentation
```

## Usage Examples

### Sample Questions to Try:
- "What programming courses are available?"
- "I want to learn machine learning"
- "What are the prerequisites for advanced AI courses?"
- "Show me data science courses"
- "What courses require CS101?"
- "Tell me about web development"

## Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem:** `ModuleNotFoundError: No module named 'xyz'`
**Solution:** 
```bash
pip install -r requirements.txt
```

#### 2. Database Connection Error
**Problem:** Can't connect to PostgreSQL
**Solution:** 
- Check if PostgreSQL is running
- Verify credentials in `.env` file
- Try the Docker setup: `docker-compose up postgres -d`

#### 3. Model Loading Issues
**Problem:** Transformer models fail to load
**Solution:** 
- Ensure you have sufficient RAM (4GB+ recommended)
- Use the offline demo for testing: `python3 demo_offline.py`
- Check internet connection for model downloads

#### 4. Streamlit Port Issues
**Problem:** Port 8501 already in use
**Solution:** 
```bash
streamlit run app.py --server.port 8502
```

### Performance Tips

1. **First Run:** Model downloads may take time
2. **Memory:** Close other applications if running out of RAM
3. **GPU:** CUDA-enabled GPU will significantly speed up LLM inference
4. **Database:** Index optimization is included in setup script

## Development

### Adding New Courses
Add courses directly to the database:
```sql
INSERT INTO courses (course_code, course_name, description, prerequisites, credits, department) 
VALUES ('NEW101', 'New Course', 'Course description', 'Prerequisites', 3, 'Department');
```

### Customizing the LLM
Edit `config.py` to change the model:
```python
LLM_MODEL = "your-preferred-model"
```

### Modifying the UI
The Streamlit interface is in `app.py`. Customize colors, layout, and components as needed.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is open source. See LICENSE file for details.

## Support

For issues and questions:
1. Check this setup guide
2. Review the troubleshooting section
3. Check the GitHub issues
4. Create a new issue with detailed information

---

Happy coding! 🚀