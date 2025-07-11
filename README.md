# RAG Chatbot Application

A sophisticated Retrieval-Augmented Generation (RAG) chatbot built with Snowflake Cortex Search and Mistral LLM for intelligent document processing and Q&A.


## 🚀 Features

- **Document Processing**: Upload and process PDF, TXT, and Markdown files
- **Intelligent Retrieval**: Snowflake Cortex Search for semantic document search
- **Advanced Generation**: Mistral LLM for contextual response generation
- **Interactive UI**: Modern Streamlit interface with chat history
- **Follow-up Questions**: AI-generated suggested questions
- **Health Monitoring**: System status and component health checks
- **Document Analytics**: Statistics and insights about your knowledge base

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │  RAG Pipeline   │    │   Snowflake     │
│                 │◄──►│                 │◄──►│  Cortex Search  │
│   Chat Interface│    │  Orchestration  │    │   Data Storage  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Mistral LLM   │
                       │   Generation    │
                       └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Snowflake account with Cortex Search enabled
- Mistral API key
- Virtual environment (recommended)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ragchatbot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Snowflake Database

1. Connect to your Snowflake account
2. Run the SQL script to create the database structure:

```bash
# Execute the SQL commands in config/snowflake_setup.sql
```

**Important**: Update the `YOUR_WAREHOUSE` placeholder in the SQL script with your actual warehouse name.

### 5. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account_name
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=RAG_CHATBOT_DB
SNOWFLAKE_SCHEMA=PUBLIC

# Mistral API Configuration
MISTRAL_API_KEY=your_mistral_api_key

# Application Configuration (Optional)
APP_TITLE=RAG Chatbot
APP_DESCRIPTION=AI-powered document Q&A system using Snowflake Cortex Search and Mistral LLM
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_RETRIEVED_DOCS=5
```

## 🚀 Usage

### Running the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Using the Chatbot

1. **Upload Documents**: Use the sidebar to upload PDF, TXT, or Markdown files
2. **Ask Questions**: Type questions about your uploaded documents
3. **View Sources**: Check which documents were used to answer your questions
4. **Follow-up**: Click on suggested follow-up questions for deeper exploration
5. **Monitor Health**: Use the health check to ensure all components are working

### Example Workflow

1. Upload a document (e.g., company policy manual)
2. Ask: "What is the vacation policy?"
3. Review the response and source documents
4. Click on follow-up questions like "How many vacation days do employees get?"

## 📁 Project Structure

```
ragchatbot/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── snowflake_client.py    # Snowflake database operations
│   ├── mistral_client.py      # Mistral LLM integration
│   ├── document_processor.py  # Document ingestion and chunking
│   └── rag_pipeline.py        # Main RAG orchestration
├── config/
│   └── snowflake_setup.sql    # Database initialization script
├── app.py                     # Streamlit application
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## ⚙️ Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CHUNK_SIZE` | Text chunk size for processing | 1000 |
| `CHUNK_OVERLAP` | Overlap between chunks | 200 |
| `MAX_RETRIEVED_DOCS` | Max documents to retrieve | 5 |

### Snowflake Configuration

- Ensure your Snowflake account has Cortex Search enabled
- The warehouse should have appropriate compute resources
- Grant necessary permissions for the user account

### Mistral Configuration

- Sign up for Mistral API access
- Use the `mistral-large-latest` model for best results
- Monitor API usage and rate limits

## 🔧 Troubleshooting

### Common Issues

1. **Snowflake Connection Failed**
   - Verify account, username, and password
   - Check warehouse name and permissions
   - Ensure Cortex Search is enabled

2. **Mistral API Errors**
   - Verify API key is correct
   - Check API quota and rate limits
   - Ensure internet connectivity

3. **Document Upload Issues**
   - Check file format (PDF, TXT, MD only)
   - Verify file is not corrupted
   - Ensure sufficient disk space

4. **No Search Results**
   - Upload more relevant documents
   - Try different question phrasings
   - Check if Cortex Search service is running

### Debug Mode

Enable debug logging by setting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔒 Security Considerations

- Store sensitive credentials in environment variables
- Use Snowflake role-based access control
- Monitor API key usage
- Implement proper error handling for production use

## 📊 Performance Tips

- **Document Size**: Keep documents under 10MB for better processing
- **Chunk Size**: Adjust based on document type (technical docs: 500-800, general: 1000-1500)
- **Warehouse Size**: Use appropriate Snowflake warehouse size for your workload
- **Caching**: Streamlit caches the RAG pipeline for better performance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙋‍♂️ Support

For questions and support:
- Check the troubleshooting section
- Review Snowflake Cortex Search documentation
- Consult Mistral API documentation
- Create an issue in the repository

## 🚀 Future Enhancements

- [ ] Support for more document formats (DOCX, PPT)
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] User authentication and sessions
- [ ] Document versioning
- [ ] API endpoints for integration
- [ ] Batch document processing
- [ ] Custom embedding models

---

**Built with ❤️ using Snowflake Cortex Search, Mistral LLM, and Streamlit** 