# RAG Chatbot MCP Server Guide

## Overview

This document provides a comprehensive guide to the Model Context Protocol (MCP) server built for the RAG Chatbot application. The MCP server provides standardized interfaces for AI systems to interact with document processing, search, and generation capabilities.

## Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Running the Server](#running-the-server)
5. [MCP Endpoints](#mcp-endpoints)
6. [Tools](#tools)
7. [Resources](#resources)
8. [Prompts](#prompts)
9. [Client Usage](#client-usage)
10. [Examples](#examples)
11. [Troubleshooting](#troubleshooting)

## What is MCP?

The Model Context Protocol (MCP) is an open standard that enables AI systems to securely and dynamically connect with external data sources, tools, and services. Think of it as the "USB-C for AI" - providing a universal interface for AI applications to interact with various systems.

### Key Benefits

- **Standardization**: Unified interface across different tools and services
- **Dynamic Discovery**: AI systems can discover and use new capabilities at runtime
- **Security**: Built-in access controls and permission management
- **Interoperability**: Works across different AI models and platforms
- **Modularity**: Composable tools that can be combined for complex workflows

## Architecture

The MCP server implements the following components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Client     │◄──►│   MCP Server    │◄──►│   RAG Pipeline  │
│   (Claude, etc) │    │   (FastAPI)     │    │   Components    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Snowflake DB  │
                       │   Document Store│
                       └─────────────────┘
```

### Components

- **MCP Server**: FastAPI-based server implementing MCP specification
- **Tools**: Executable functions for document processing, search, and queries
- **Resources**: Structured data access for system information and documents
- **Prompts**: Reusable prompt templates for common operations
- **RAG Integration**: Direct integration with existing RAG pipeline

## Installation

### Prerequisites

- Python 3.8+
- All dependencies from the main RAG application
- FastAPI and related MCP dependencies

### Install Dependencies

```bash
pip install -r requirements.txt
```

The requirements.txt includes:
- `fastapi>=0.104.0` - Web framework for the MCP server
- `uvicorn[standard]>=0.24.0` - ASGI server
- `pydantic>=2.5.0` - Data validation
- `aiohttp>=3.9.0` - For client examples

## Running the Server

### Basic Usage

```bash
# Run the MCP server
python mcp_server.py
```

The server will start on `http://localhost:8000` by default.

### Configuration

The server automatically detects and integrates with available RAG components:
- RAG Pipeline
- Document Processor
- Snowflake Client
- Mistral Client

If components are not available, the server runs in standalone mode with limited functionality.

### Environment Variables

Ensure your `.env` file contains the necessary configuration:

```bash
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=RAG_CHATBOT_DB
SNOWFLAKE_SCHEMA=PUBLIC

# Mistral API Configuration
MISTRAL_API_KEY=your_mistral_api_key

# Application Configuration
APP_TITLE=RAG Chatbot
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_RETRIEVED_DOCS=5
```

## MCP Endpoints

### Discovery Endpoint

**GET** `/.well-known/mcp/manifest.json`

Returns the MCP manifest describing server capabilities, tools, resources, and prompts.

### Health Check

**GET** `/health`

Returns server health status and component availability.

### Tools Endpoints

- **GET** `/mcp/tools/list` - List all available tools
- **POST** `/mcp/tools/call` - Execute a tool

### Resources Endpoints

- **GET** `/mcp/resources/list` - List all available resources
- **POST** `/mcp/resources/read` - Read a specific resource

### Prompts Endpoints

- **GET** `/mcp/prompts/list` - List all available prompts
- **POST** `/mcp/prompts/get` - Get a specific prompt

## Tools

The MCP server provides the following tools:

### 1. process_document

Process and ingest a document into the knowledge base.

**Parameters:**
- `file_path` (string, required): Path to the document file
- `metadata` (object, optional): Document metadata (title, author, tags)

**Example:**
```json
{
  "name": "process_document",
  "arguments": {
    "file_path": "/path/to/document.pdf",
    "metadata": {
      "title": "AI Research Paper",
      "author": "Dr. Smith",
      "tags": ["AI", "research", "machine-learning"]
    }
  }
}
```

### 2. search_documents

Search for relevant documents in the knowledge base.

**Parameters:**
- `query` (string, required): Search query
- `max_results` (integer, optional): Maximum results to return (default: 5)
- `similarity_threshold` (number, optional): Minimum similarity score (default: 0.7)

**Example:**
```json
{
  "name": "search_documents",
  "arguments": {
    "query": "machine learning algorithms",
    "max_results": 10,
    "similarity_threshold": 0.8
  }
}
```

### 3. rag_query

Perform a complete RAG query with retrieval and generation.

**Parameters:**
- `question` (string, required): Question to answer
- `conversation_history` (array, optional): Previous conversation messages
- `max_retrieved_docs` (integer, optional): Maximum documents to retrieve (default: 5)

**Example:**
```json
{
  "name": "rag_query",
  "arguments": {
    "question": "What are the benefits of transformer models?",
    "conversation_history": [
      {"role": "user", "content": "Tell me about AI"},
      {"role": "assistant", "content": "AI is artificial intelligence..."}
    ],
    "max_retrieved_docs": 3
  }
}
```

### 4. query_database

Execute a query against the Snowflake database.

**Parameters:**
- `query` (string, required): SQL query to execute
- `limit` (integer, optional): Maximum rows to return (default: 100)

**Example:**
```json
{
  "name": "query_database",
  "arguments": {
    "query": "SELECT COUNT(*) FROM documents WHERE source_file LIKE '%.pdf'",
    "limit": 50
  }
}
```

### 5. get_system_status

Get the current status of all system components.

**Parameters:** None

**Example:**
```json
{
  "name": "get_system_status",
  "arguments": {}
}
```

### 6. get_document_stats

Get statistics about the document collection.

**Parameters:**
- `include_details` (boolean, optional): Include detailed statistics (default: false)

**Example:**
```json
{
  "name": "get_document_stats",
  "arguments": {
    "include_details": true
  }
}
```

## Resources

Resources provide read-only access to structured data:

### 1. rag://documents/list

List of all documents in the knowledge base.

### 2. rag://system/config

Current system configuration and settings.

### 3. rag://stats/summary

Summary statistics about the system.

**Example Usage:**
```json
{
  "uri": "rag://system/config"
}
```

## Prompts

Prompts provide reusable templates for common operations:

### 1. document_summary

Generate a summary of a document.

**Arguments:**
- `document_content` (required): The document content to summarize
- `max_length` (optional): Maximum length of the summary

### 2. question_answering

Answer a question based on retrieved context.

**Arguments:**
- `question` (required): The question to answer
- `context` (required): Retrieved context documents

### 3. follow_up_questions

Generate follow-up questions based on a conversation.

**Arguments:**
- `conversation` (required): The conversation history
- `num_questions` (optional): Number of questions to generate

**Example Usage:**
```json
{
  "name": "document_summary",
  "arguments": {
    "document_content": "This is a research paper about...",
    "max_length": "brief"
  }
}
```

## Client Usage

### Using the Example Client

The repository includes a comprehensive client example (`mcp_client_example.py`):

```bash
# Run demo mode
python mcp_client_example.py

# Run interactive mode
python mcp_client_example.py --interactive

# Use custom server URL
python mcp_client_example.py --server http://your-server:8000
```

### Programmatic Usage

```python
import asyncio
from mcp_client_example import MCPClient

async def example_usage():
    async with MCPClient("http://localhost:8000") as client:
        # Check server health
        health = await client.health_check()
        print(f"Server status: {health['status']}")
        
        # List available tools
        tools = await client.list_tools()
        for tool in tools:
            print(f"Tool: {tool['name']}")
        
        # Call a tool
        result = await client.call_tool("get_system_status")
        print(f"System status: {result}")
        
        # Read a resource
        config = await client.read_resource("rag://system/config")
        print(f"System config: {config}")

asyncio.run(example_usage())
```

## Examples

### Example 1: Document Processing Workflow

```python
async def process_and_search():
    async with MCPClient() as client:
        # Process a document
        result = await client.call_tool("process_document", {
            "file_path": "/path/to/document.pdf",
            "metadata": {"title": "Research Paper"}
        })
        
        # Search for related content
        search_result = await client.call_tool("search_documents", {
            "query": "machine learning",
            "max_results": 5
        })
        
        # Perform RAG query
        rag_result = await client.call_tool("rag_query", {
            "question": "What are the main findings?"
        })
```

### Example 2: System Monitoring

```python
async def monitor_system():
    async with MCPClient() as client:
        # Check system health
        health = await client.health_check()
        
        # Get detailed system status
        status = await client.call_tool("get_system_status")
        
        # Get document statistics
        stats = await client.call_tool("get_document_stats", {
            "include_details": True
        })
        
        # Read system configuration
        config = await client.read_resource("rag://system/config")
```

### Example 3: Using Prompts

```python
async def use_prompts():
    async with MCPClient() as client:
        # Generate document summary prompt
        summary_prompt = await client.get_prompt("document_summary", {
            "document_content": "Long document content here...",
            "max_length": "concise"
        })
        
        # Generate Q&A prompt
        qa_prompt = await client.get_prompt("question_answering", {
            "question": "What is the main topic?",
            "context": "Retrieved context documents..."
        })
```

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check that all dependencies are installed
   - Verify port 8000 is available
   - Check for import errors in the logs

2. **RAG components not available**
   - Ensure environment variables are set correctly
   - Check Snowflake and Mistral API credentials
   - Verify database connection

3. **Tool execution errors**
   - Check tool arguments match the expected schema
   - Verify required components are initialized
   - Review server logs for detailed error messages

4. **Resource access errors**
   - Ensure the resource URI is correct
   - Check database connectivity for data resources
   - Verify permissions

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Check

Always start troubleshooting with a health check:

```bash
curl http://localhost:8000/health
```

### Logs

Check server logs for detailed error information:

```bash
python mcp_server.py 2>&1 | tee server.log
```

## Security Considerations

- The server runs with CORS enabled for development
- Database queries are limited by default
- File operations are restricted to specified paths
- Consider adding authentication for production use
- Validate all input parameters
- Monitor resource usage and rate limiting

## Future Enhancements

- Authentication and authorization
- Rate limiting and quotas
- Caching for improved performance
- WebSocket support for real-time updates
- Plugin system for custom tools
- Monitoring and metrics collection
- Docker containerization

## Support

For issues and questions:
- Check the troubleshooting section
- Review server logs
- Consult the MCP specification
- Create an issue in the repository

---

**Built with ❤️ using FastAPI and the Model Context Protocol**