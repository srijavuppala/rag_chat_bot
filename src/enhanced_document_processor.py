import os
import csv
import io
from typing import List, Dict, Any, Optional
import warnings
import PyPDF2
from unstructured.partition.auto import partition
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from transformers import pipeline
import requests
import nltk
from src.config import Config
from src.snowflake_client import SnowflakeClient

# Suppress warnings for cleaner output
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    message=r".*clean_up_tokenization_spaces.*"
)

# Set environment variables for OpenMP
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

class EnhancedDocumentProcessor:
    """Enhanced document processor with multi-format support and summarization"""
    
    def __init__(self, snowflake_client: SnowflakeClient):
        self.snowflake_client = snowflake_client
        
        # Enhanced text splitter with better parameters
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Smaller chunks for better retrieval
            chunk_overlap=100,  # Good overlap for context preservation
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize summarizer (try local first, fallback to API)
        self.local_summarizer = None
        self.huggingface_api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        self.huggingface_headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
        
        self._initialize_summarizer()
    
    def _initialize_summarizer(self):
        """Initialize local summarizer model with fallback to API"""
        try:
            model_name = "sshleifer/distilbart-cnn-12-6"
            self.local_summarizer = pipeline("summarization", model=model_name)
            print("✅ Local summarizer model loaded successfully")
        except Exception as e:
            print(f"⚠️ Failed to load local summarizer model: {e}")
            print("📡 Will use Hugging Face API for summarization")
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Enhanced PDF text extraction with better error handling"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if not text.strip():
                raise ValueError("The PDF file appears to be empty or contains no extractable text")
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {e}")
    
    def extract_text_from_txt(self, txt_file) -> str:
        """Enhanced text file processing"""
        try:
            content = txt_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            if not content.strip():
                raise ValueError("The text file is empty")
            
            return content.strip()
            
        except Exception as e:
            raise Exception(f"Error extracting text from TXT file: {e}")
    
    def extract_text_from_csv(self, csv_file) -> str:
        """Extract text from CSV file"""
        try:
            content = csv_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            
            csv_reader = csv.reader(io.StringIO(content))
            text_rows = []
            
            for row in csv_reader:
                if row:  # Skip empty rows
                    text_rows.append(", ".join(row))
            
            text = "\n".join(text_rows)
            
            if not text.strip():
                raise ValueError("The CSV file is empty or contains no readable data")
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Error extracting text from CSV file: {e}")
    
    def extract_text_from_docx(self, docx_file) -> str:
        """Extract text from DOCX file using unstructured"""
        try:
            # Reset file pointer to beginning
            docx_file.seek(0)
            
            # Use unstructured to partition the document
            elements = partition(file=docx_file)
            text = "\n".join(str(element) for element in elements)
            
            if not text.strip():
                raise ValueError("The DOCX file is empty or contains no readable text")
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX file: {e}")
    
    def process_uploaded_file(self, uploaded_file) -> str:
        """Enhanced file processing with support for multiple formats"""
        file_type = uploaded_file.type
        filename = uploaded_file.name.lower()
        
        try:
            if file_type == "application/pdf":
                return self.extract_text_from_pdf(uploaded_file)
            
            elif file_type == "text/plain":
                return self.extract_text_from_txt(uploaded_file)
            
            elif file_type == "text/csv":
                return self.extract_text_from_csv(uploaded_file)
            
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return self.extract_text_from_docx(uploaded_file)
            
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            raise Exception(f"Failed to process file '{uploaded_file.name}': {e}")
    
    def summarize_text(self, text: str, min_length: int = 10, max_length: int = 150) -> Optional[str]:
        """Summarize text using local model or API fallback"""
        max_input_length = 1024  # Maximum input length for BART model
        
        # Truncate input text if necessary
        if len(text.split()) > max_input_length:
            text = ' '.join(text.split()[:max_input_length])
            print("⚠️ Input text was truncated for summarization")
        
        # Calculate appropriate max_length
        input_length = len(text.split())
        max_length = min(int(input_length * 0.7), max_length, max_input_length)
        
        # Try local summarizer first
        if self.local_summarizer:
            try:
                summary = self.local_summarizer(
                    text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False,
                    clean_up_tokenization_spaces=True
                )
                return summary[0].get('summary_text', "")
            except Exception as e:
                print(f"⚠️ Local summarization failed: {e}")
        
        # Fallback to Hugging Face API
        return self._summarize_with_api(text, min_length, max_length)
    
    def _summarize_with_api(self, text: str, min_length: int, max_length: int) -> Optional[str]:
        """Summarize text using Hugging Face API"""
        try:
            payload = {
                "inputs": text,
                "parameters": {"min_length": min_length, "max_length": max_length}
            }
            
            response = requests.post(self.huggingface_api_url, headers=self.huggingface_headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and result:
                return result[0].get('summary_text', "")
            
            return ""
            
        except Exception as e:
            print(f"⚠️ API summarization failed: {e}")
            return ""
    
    def create_enhanced_chunks(self, text: str, metadata: Dict = None) -> List[Document]:
        """Create enhanced chunks as LangChain Document objects"""
        try:
            # Split text into chunks
            text_chunks = self.text_splitter.split_text(text)
            
            # Create Document objects with metadata
            documents = []
            base_metadata = metadata or {}
            
            for i, chunk in enumerate(text_chunks):
                if chunk.strip():  # Only process non-empty chunks
                    chunk_metadata = {
                        "chunk_index": i,
                        "chunk_size": len(chunk),
                        "total_chunks": len(text_chunks),
                        **base_metadata
                    }
                    
                    # Create summary for the chunk if it's long enough
                    summary = ""
                    if len(chunk.split()) > 50:  # Only summarize substantial chunks
                        summary = self.summarize_text(chunk)
                    
                    # Use summary if available, otherwise use original text
                    content = summary if summary and summary.strip() else chunk
                    
                    documents.append(Document(
                        page_content=content,
                        metadata=chunk_metadata
                    ))
            
            return documents
            
        except Exception as e:
            print(f"Error creating enhanced chunks: {e}")
            return []
    
    def ingest_document_enhanced(self, uploaded_file, metadata: Dict = None, use_summarization: bool = True) -> bool:
        """Enhanced document ingestion with summarization"""
        try:
            print(f"🔄 Processing document: {uploaded_file.name}")
            
            # Extract text from uploaded file
            text_content = self.process_uploaded_file(uploaded_file)
            
            if not text_content:
                print("❌ No text content extracted from file")
                return False
            
            print(f"✅ Extracted {len(text_content)} characters from {uploaded_file.name}")
            
            # Prepare document metadata
            doc_metadata = {
                "filename": uploaded_file.name,
                "file_type": uploaded_file.type,
                "file_size": len(text_content),
                "processed_with_summarization": use_summarization,
                **(metadata or {})
            }
            
            # Insert document into database (without metadata for now due to VARIANT issues)
            doc_id = self.snowflake_client.insert_document(
                filename=uploaded_file.name,
                content=text_content,
                metadata=None  # Temporarily disabled metadata due to VARIANT issues
            )
            
            if not doc_id:
                print("❌ Failed to insert document into database")
                return False
            
            print(f"✅ Document inserted with ID: {doc_id}")
            
            # Create enhanced chunks
            if use_summarization:
                document_objects = self.create_enhanced_chunks(text_content, doc_metadata)
                print(f"📄 Created {len(document_objects)} summarized chunks")
            else:
                # Use regular chunking without summarization
                chunks = self.text_splitter.split_text(text_content)
                document_objects = [
                    Document(
                        page_content=chunk,
                        metadata={**doc_metadata, "chunk_index": i}
                    ) for i, chunk in enumerate(chunks) if chunk.strip()
                ]
                print(f"📄 Created {len(document_objects)} regular chunks")
            
            # Convert Document objects to format expected by Snowflake client
            chunks_for_db = []
            for doc_obj in document_objects:
                chunks_for_db.append({
                    "document_id": doc_id,
                    "text": doc_obj.page_content,
                    "metadata": doc_obj.metadata,
                    "index": doc_obj.metadata.get("chunk_index", 0)
                })
            
            # Insert chunks into database
            success = self.snowflake_client.insert_document_chunks(chunks_for_db)
            
            if success:
                print(f"✅ Successfully ingested document: {uploaded_file.name}")
                print(f"📊 Created {len(chunks_for_db)} chunks")
                return True
            else:
                print("❌ Failed to insert document chunks")
                return False
                
        except Exception as e:
            print(f"❌ Document ingestion failed: {e}")
            return False
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return [
            "application/pdf",
            "text/plain", 
            "text/csv",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
    
    def get_format_description(self) -> str:
        """Get human-readable description of supported formats"""
        return "Supported formats: PDF, TXT, CSV, DOCX" 