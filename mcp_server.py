#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server
A comprehensive MCP server that integrates with the RAG chatbot application
to provide standardized interfaces for AI systems.
"""

import json
import logging
import asyncio
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import traceback

# Third-party imports
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# Local imports (will be conditionally imported)
try:
    from src.rag_pipeline import RAGPipeline
    from src.config import Config
    from src.document_processor import DocumentProcessor
    from src.snowflake_client import SnowflakeClient
    from src.mistral_client import MistralClient
    HAS_RAG_COMPONENTS = True
except ImportError:
    HAS_RAG_COMPONENTS = False
    print("Warning: RAG components not available. Running in standalone mode.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP Protocol Models
@dataclass
class MCPTool:
    """Represents an MCP tool with its metadata and functionality."""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    
class MCPResource(BaseModel):
    """Represents an MCP resource."""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None

class MCPPrompt(BaseModel):
    """Represents an MCP prompt template."""
    name: str
    description: str
    arguments: List[Dict[str, Any]] = []

class ToolCall(BaseModel):
    """Request model for tool calls."""
    name: str
    arguments: Dict[str, Any] = {}

class ToolResponse(BaseModel):
    """Response model for tool calls."""
    content: List[Dict[str, Any]]
    isError: bool = False

class ResourceRequest(BaseModel):
    """Request model for resource access."""
    uri: str

class PromptRequest(BaseModel):
    """Request model for prompt requests."""
    name: str
    arguments: Dict[str, Any] = {}

class PromptResponse(BaseModel):
    """Response model for prompt requests."""
    description: str
    messages: List[Dict[str, Any]]

class MCPServer:
    """Main MCP Server class implementing the Model Context Protocol."""
    
    def __init__(self):
        self.app = FastAPI(
            title="RAG Chatbot MCP Server",
            description="Model Context Protocol server for RAG chatbot capabilities",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize components
        self.rag_pipeline = None
        self.document_processor = None
        self.snowflake_client = None
        self.mistral_client = None
        
        # Initialize RAG components if available
        if HAS_RAG_COMPONENTS:
            try:
                self.rag_pipeline = RAGPipeline()
                self.document_processor = DocumentProcessor()
                if hasattr(Config, 'SNOWFLAKE_ACCOUNT'):
                    self.snowflake_client = SnowflakeClient()
                if hasattr(Config, 'MISTRAL_API_KEY'):
                    self.mistral_client = MistralClient()
                logger.info("RAG components initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize some RAG components: {e}")
        
        # Setup routes
        self._setup_routes()
        
        # Define available tools
        self.tools = self._define_tools()
        
        # Define available resources
        self.resources = self._define_resources()
        
        # Define available prompts
        self.prompts = self._define_prompts()
    
    def _setup_routes(self):
        """Setup FastAPI routes for MCP endpoints."""
        
        # MCP Discovery endpoint - required by MCP specification
        @self.app.get("/.well-known/mcp/manifest.json")
        async def get_manifest():
            """Return the MCP manifest describing server capabilities."""
            return self._generate_manifest()
        
        # MCP Tools endpoints
        @self.app.get("/mcp/tools/list")
        async def list_tools():
            """List all available tools."""
            return {"tools": [asdict(tool) for tool in self.tools]}
        
        @self.app.post("/mcp/tools/call")
        async def call_tool(request: ToolCall):
            """Execute a tool with the given arguments."""
            try:
                result = await self._execute_tool(request.name, request.arguments)
                return ToolResponse(content=result, isError=False)
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return ToolResponse(
                    content=[{"type": "text", "text": f"Error: {str(e)}"}],
                    isError=True
                )
        
        # MCP Resources endpoints
        @self.app.get("/mcp/resources/list")
        async def list_resources():
            """List all available resources."""
            return {"resources": [resource.dict() for resource in self.resources]}
        
        @self.app.post("/mcp/resources/read")
        async def read_resource(request: ResourceRequest):
            """Read a specific resource."""
            try:
                content = await self._read_resource(request.uri)
                return {"contents": content}
            except Exception as e:
                logger.error(f"Resource read error: {e}")
                raise HTTPException(status_code=404, detail=str(e))
        
        # MCP Prompts endpoints
        @self.app.get("/mcp/prompts/list")
        async def list_prompts():
            """List all available prompts."""
            return {"prompts": [prompt.dict() for prompt in self.prompts]}
        
        @self.app.post("/mcp/prompts/get")
        async def get_prompt(request: PromptRequest):
            """Get a specific prompt with arguments."""
            try:
                response = await self._get_prompt(request.name, request.arguments)
                return response.dict()
            except Exception as e:
                logger.error(f"Prompt error: {e}")
                raise HTTPException(status_code=404, detail=str(e))
        
        # Health check endpoint
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "rag_pipeline": self.rag_pipeline is not None,
                    "document_processor": self.document_processor is not None,
                    "snowflake_client": self.snowflake_client is not None,
                    "mistral_client": self.mistral_client is not None,
                }
            }
            return status
        
        # Document upload endpoint (additional functionality)
        @self.app.post("/documents/upload")
        async def upload_document(file: UploadFile = File(...)):
            """Upload and process a document."""
            if not self.document_processor:
                raise HTTPException(status_code=503, detail="Document processor not available")
            
            try:
                # Save uploaded file temporarily
                temp_path = f"/tmp/{file.filename}"
                with open(temp_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                
                # Process document
                result = self.document_processor.process_document(temp_path)
                
                # Clean up
                os.unlink(temp_path)
                
                return {"message": "Document processed successfully", "result": result}
            except Exception as e:
                logger.error(f"Document upload error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _generate_manifest(self) -> Dict[str, Any]:
        """Generate the MCP manifest file."""
        return {
            "schemaVersion": "2025-03-26",
            "name": "rag-chatbot-mcp-server",
            "version": "1.0.0",
            "description": "MCP server providing RAG chatbot capabilities including document processing, search, and generation",
            "author": "RAG Chatbot Team",
            "license": "MIT",
            "homepage": "https://github.com/your-org/rag-chatbot",
            "capabilities": {
                "tools": {
                    "listChanged": True
                },
                "resources": {
                    "subscribe": True,
                    "listChanged": True
                },
                "prompts": {
                    "listChanged": True
                }
            },
            "tools": [asdict(tool) for tool in self.tools],
            "resources": [resource.dict() for resource in self.resources],
            "prompts": [prompt.dict() for prompt in self.prompts]
        }
    
    def _define_tools(self) -> List[MCPTool]:
        """Define available MCP tools."""
        tools = [
            # Document processing tools
            MCPTool(
                name="process_document",
                description="Process and ingest a document into the knowledge base",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the document file"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Optional metadata for the document",
                            "properties": {
                                "title": {"type": "string"},
                                "author": {"type": "string"},
                                "tags": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            
            # Search and retrieval tools
            MCPTool(
                name="search_documents",
                description="Search for relevant documents in the knowledge base",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 5
                        },
                        "similarity_threshold": {
                            "type": "number",
                            "description": "Minimum similarity score for results",
                            "default": 0.7
                        }
                    },
                    "required": ["query"]
                }
            ),
            
            # RAG query tool
            MCPTool(
                name="rag_query",
                description="Perform a complete RAG query with retrieval and generation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "Question to answer using the knowledge base"
                        },
                        "conversation_history": {
                            "type": "array",
                            "description": "Previous conversation messages",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "role": {"type": "string", "enum": ["user", "assistant"]},
                                    "content": {"type": "string"}
                                }
                            }
                        },
                        "max_retrieved_docs": {
                            "type": "integer",
                            "description": "Maximum number of documents to retrieve",
                            "default": 5
                        }
                    },
                    "required": ["question"]
                }
            ),
            
            # Database query tool
            MCPTool(
                name="query_database",
                description="Execute a query against the Snowflake database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL query to execute"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of rows to return",
                            "default": 100
                        }
                    },
                    "required": ["query"]
                }
            ),
            
            # System information tools
            MCPTool(
                name="get_system_status",
                description="Get the current status of all system components",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            ),
            
            # Document statistics tool
            MCPTool(
                name="get_document_stats",
                description="Get statistics about the document collection",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "include_details": {
                            "type": "boolean",
                            "description": "Include detailed statistics",
                            "default": False
                        }
                    }
                }
            )
        ]
        
        return tools
    
    def _define_resources(self) -> List[MCPResource]:
        """Define available MCP resources."""
        resources = [
            MCPResource(
                uri="rag://documents/list",
                name="Document List",
                description="List of all documents in the knowledge base",
                mimeType="application/json"
            ),
            MCPResource(
                uri="rag://system/config",
                name="System Configuration",
                description="Current system configuration and settings",
                mimeType="application/json"
            ),
            MCPResource(
                uri="rag://stats/summary",
                name="System Statistics",
                description="Summary statistics about the system",
                mimeType="application/json"
            )
        ]
        
        return resources
    
    def _define_prompts(self) -> List[MCPPrompt]:
        """Define available MCP prompts."""
        prompts = [
            MCPPrompt(
                name="document_summary",
                description="Generate a summary of a document",
                arguments=[
                    {
                        "name": "document_content",
                        "description": "The content of the document to summarize",
                        "required": True
                    },
                    {
                        "name": "max_length",
                        "description": "Maximum length of the summary",
                        "required": False
                    }
                ]
            ),
            MCPPrompt(
                name="question_answering",
                description="Answer a question based on retrieved context",
                arguments=[
                    {
                        "name": "question",
                        "description": "The question to answer",
                        "required": True
                    },
                    {
                        "name": "context",
                        "description": "Retrieved context documents",
                        "required": True
                    }
                ]
            ),
            MCPPrompt(
                name="follow_up_questions",
                description="Generate follow-up questions based on a conversation",
                arguments=[
                    {
                        "name": "conversation",
                        "description": "The conversation history",
                        "required": True
                    },
                    {
                        "name": "num_questions",
                        "description": "Number of follow-up questions to generate",
                        "required": False
                    }
                ]
            )
        ]
        
        return prompts
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a specific tool with given arguments."""
        if tool_name == "process_document":
            return await self._process_document(arguments)
        elif tool_name == "search_documents":
            return await self._search_documents(arguments)
        elif tool_name == "rag_query":
            return await self._rag_query(arguments)
        elif tool_name == "query_database":
            return await self._query_database(arguments)
        elif tool_name == "get_system_status":
            return await self._get_system_status(arguments)
        elif tool_name == "get_document_stats":
            return await self._get_document_stats(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _process_document(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a document and add it to the knowledge base."""
        if not self.document_processor:
            raise RuntimeError("Document processor not available")
        
        file_path = arguments["file_path"]
        metadata = arguments.get("metadata", {})
        
        try:
            result = self.document_processor.process_document(file_path, metadata)
            return [{"type": "text", "text": f"Document processed successfully: {result}"}]
        except Exception as e:
            raise RuntimeError(f"Failed to process document: {str(e)}")
    
    async def _search_documents(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for documents in the knowledge base."""
        if not self.rag_pipeline:
            raise RuntimeError("RAG pipeline not available")
        
        query = arguments["query"]
        max_results = arguments.get("max_results", 5)
        similarity_threshold = arguments.get("similarity_threshold", 0.7)
        
        try:
            results = self.rag_pipeline.search_documents(
                query, 
                max_results=max_results,
                similarity_threshold=similarity_threshold
            )
            
            return [{
                "type": "text",
                "text": json.dumps(results, indent=2)
            }]
        except Exception as e:
            raise RuntimeError(f"Failed to search documents: {str(e)}")
    
    async def _rag_query(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform a complete RAG query."""
        if not self.rag_pipeline:
            raise RuntimeError("RAG pipeline not available")
        
        question = arguments["question"]
        conversation_history = arguments.get("conversation_history", [])
        max_retrieved_docs = arguments.get("max_retrieved_docs", 5)
        
        try:
            response = self.rag_pipeline.query(
                question,
                conversation_history=conversation_history,
                max_retrieved_docs=max_retrieved_docs
            )
            
            return [{
                "type": "text",
                "text": json.dumps(response, indent=2)
            }]
        except Exception as e:
            raise RuntimeError(f"Failed to perform RAG query: {str(e)}")
    
    async def _query_database(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a database query."""
        if not self.snowflake_client:
            raise RuntimeError("Snowflake client not available")
        
        query = arguments["query"]
        limit = arguments.get("limit", 100)
        
        try:
            # Add LIMIT clause if not present
            if "LIMIT" not in query.upper():
                query += f" LIMIT {limit}"
            
            results = self.snowflake_client.execute_query(query)
            
            return [{
                "type": "text",
                "text": json.dumps(results, indent=2, default=str)
            }]
        except Exception as e:
            raise RuntimeError(f"Failed to execute database query: {str(e)}")
    
    async def _get_system_status(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get system status information."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "components": {
                "rag_pipeline": {
                    "available": self.rag_pipeline is not None,
                    "status": "healthy" if self.rag_pipeline else "unavailable"
                },
                "document_processor": {
                    "available": self.document_processor is not None,
                    "status": "healthy" if self.document_processor else "unavailable"
                },
                "snowflake_client": {
                    "available": self.snowflake_client is not None,
                    "status": "healthy" if self.snowflake_client else "unavailable"
                },
                "mistral_client": {
                    "available": self.mistral_client is not None,
                    "status": "healthy" if self.mistral_client else "unavailable"
                }
            }
        }
        
        # Test connections if available
        if self.snowflake_client:
            try:
                self.snowflake_client.test_connection()
                status["components"]["snowflake_client"]["status"] = "healthy"
            except Exception as e:
                status["components"]["snowflake_client"]["status"] = f"error: {str(e)}"
        
        return [{
            "type": "text",
            "text": json.dumps(status, indent=2)
        }]
    
    async def _get_document_stats(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get document statistics."""
        include_details = arguments.get("include_details", False)
        
        if not self.snowflake_client:
            raise RuntimeError("Snowflake client not available")
        
        try:
            # Basic stats query
            stats_query = """
            SELECT 
                COUNT(*) as total_documents,
                COUNT(DISTINCT source_file) as unique_files,
                AVG(LENGTH(content)) as avg_content_length,
                MAX(created_at) as last_update
            FROM documents
            """
            
            stats = self.snowflake_client.execute_query(stats_query)
            
            result = {
                "basic_stats": stats[0] if stats else {},
                "generated_at": datetime.now().isoformat()
            }
            
            if include_details:
                # Detailed stats
                details_query = """
                SELECT 
                    source_file,
                    COUNT(*) as chunk_count,
                    AVG(LENGTH(content)) as avg_chunk_length,
                    MAX(created_at) as last_processed
                FROM documents
                GROUP BY source_file
                ORDER BY chunk_count DESC
                LIMIT 20
                """
                
                details = self.snowflake_client.execute_query(details_query)
                result["detailed_stats"] = details
            
            return [{
                "type": "text",
                "text": json.dumps(result, indent=2, default=str)
            }]
        except Exception as e:
            raise RuntimeError(f"Failed to get document statistics: {str(e)}")
    
    async def _read_resource(self, uri: str) -> List[Dict[str, Any]]:
        """Read a specific resource."""
        if uri == "rag://documents/list":
            return await self._get_document_list()
        elif uri == "rag://system/config":
            return await self._get_system_config()
        elif uri == "rag://stats/summary":
            return await self._get_stats_summary()
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    
    async def _get_document_list(self) -> List[Dict[str, Any]]:
        """Get list of all documents."""
        if not self.snowflake_client:
            raise RuntimeError("Snowflake client not available")
        
        try:
            query = """
            SELECT DISTINCT 
                source_file,
                COUNT(*) as chunk_count,
                MAX(created_at) as last_updated
            FROM documents
            GROUP BY source_file
            ORDER BY last_updated DESC
            """
            
            documents = self.snowflake_client.execute_query(query)
            
            return [{
                "type": "text",
                "text": json.dumps(documents, indent=2, default=str)
            }]
        except Exception as e:
            raise RuntimeError(f"Failed to get document list: {str(e)}")
    
    async def _get_system_config(self) -> List[Dict[str, Any]]:
        """Get system configuration."""
        config = {
            "app_title": getattr(Config, 'APP_TITLE', 'RAG Chatbot'),
            "chunk_size": getattr(Config, 'CHUNK_SIZE', 1000),
            "chunk_overlap": getattr(Config, 'CHUNK_OVERLAP', 200),
            "max_retrieved_docs": getattr(Config, 'MAX_RETRIEVED_DOCS', 5),
            "components_available": {
                "rag_pipeline": self.rag_pipeline is not None,
                "document_processor": self.document_processor is not None,
                "snowflake_client": self.snowflake_client is not None,
                "mistral_client": self.mistral_client is not None,
            }
        }
        
        return [{
            "type": "text",
            "text": json.dumps(config, indent=2)
        }]
    
    async def _get_stats_summary(self) -> List[Dict[str, Any]]:
        """Get summary statistics."""
        return await self._get_document_stats({"include_details": True})
    
    async def _get_prompt(self, prompt_name: str, arguments: Dict[str, Any]) -> PromptResponse:
        """Get a specific prompt with arguments."""
        if prompt_name == "document_summary":
            return await self._get_document_summary_prompt(arguments)
        elif prompt_name == "question_answering":
            return await self._get_question_answering_prompt(arguments)
        elif prompt_name == "follow_up_questions":
            return await self._get_follow_up_questions_prompt(arguments)
        else:
            raise ValueError(f"Unknown prompt: {prompt_name}")
    
    async def _get_document_summary_prompt(self, arguments: Dict[str, Any]) -> PromptResponse:
        """Get document summary prompt."""
        document_content = arguments["document_content"]
        max_length = arguments.get("max_length", "concise")
        
        prompt = f"""Please provide a {max_length} summary of the following document:

{document_content}

Summary:"""
        
        return PromptResponse(
            description="Document summary prompt",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
    
    async def _get_question_answering_prompt(self, arguments: Dict[str, Any]) -> PromptResponse:
        """Get question answering prompt."""
        question = arguments["question"]
        context = arguments["context"]
        
        prompt = f"""Based on the following context, please answer the question:

Context:
{context}

Question: {question}

Answer:"""
        
        return PromptResponse(
            description="Question answering prompt with context",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
    
    async def _get_follow_up_questions_prompt(self, arguments: Dict[str, Any]) -> PromptResponse:
        """Get follow-up questions prompt."""
        conversation = arguments["conversation"]
        num_questions = arguments.get("num_questions", 3)
        
        # Format conversation history
        conversation_text = ""
        for msg in conversation:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            conversation_text += f"{role.capitalize()}: {content}\n"
        
        prompt = f"""Based on the following conversation, generate {num_questions} relevant follow-up questions:

Conversation:
{conversation_text}

Follow-up questions:"""
        
        return PromptResponse(
            description="Follow-up questions generation prompt",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    server = MCPServer()
    return server.app

if __name__ == "__main__":
    # Create the server
    server = MCPServer()
    
    # Run the server
    uvicorn.run(
        server.app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )