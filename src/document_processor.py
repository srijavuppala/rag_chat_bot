import os
import PyPDF2
import io
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import Config
from src.snowflake_client import SnowflakeClient

class DocumentProcessor:
    """Handles document ingestion, processing, and chunking"""
    
    def __init__(self, snowflake_client: SnowflakeClient):
        self.snowflake_client = snowflake_client
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text content from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_text_from_txt(self, txt_file) -> str:
        """Extract text content from text file"""
        try:
            content = txt_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            return content.strip()
            
        except Exception as e:
            print(f"Error extracting text from TXT file: {e}")
            return ""
    
    def process_uploaded_file(self, uploaded_file) -> str:
        """Process uploaded file and extract text based on file type"""
        file_extension = uploaded_file.name.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            return self.extract_text_from_pdf(uploaded_file)
        elif file_extension in ['txt', 'md']:
            return self.extract_text_from_txt(uploaded_file)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Split text into chunks for processing"""
        chunks = self.text_splitter.split_text(text)
        
        chunked_docs = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                "chunk_index": i,
                "chunk_size": len(chunk),
                **(metadata or {})
            }
            
            chunked_docs.append({
                "text": chunk,
                "metadata": chunk_metadata,
                "index": i
            })
        
        return chunked_docs
    
    def ingest_document(self, uploaded_file, metadata: Dict = None) -> bool:
        """Complete document ingestion pipeline"""
        try:
            # Extract text from uploaded file
            text_content = self.process_uploaded_file(uploaded_file)
            
            if not text_content:
                print("No text content extracted from file")
                return False
            
            # Prepare document metadata
            doc_metadata = {
                "filename": uploaded_file.name,
                "file_type": uploaded_file.name.split('.')[-1].lower(),
                "file_size": len(text_content),
                **(metadata or {})
            }
            
            # Insert document into database
            doc_id = self.snowflake_client.insert_document(
                filename=uploaded_file.name,
                content=text_content,
                metadata=doc_metadata
            )
            
            if not doc_id:
                print("Failed to insert document into database")
                return False
            
            # Chunk the document
            chunks = self.chunk_text(text_content, doc_metadata)
            
            # Add document ID to chunks
            for chunk in chunks:
                chunk['document_id'] = doc_id
            
            # Insert chunks into database
            success = self.snowflake_client.insert_document_chunks(chunks)
            
            if success:
                print(f"Successfully ingested document: {uploaded_file.name}")
                print(f"Created {len(chunks)} chunks")
                return True
            else:
                print("Failed to insert document chunks")
                return False
                
        except Exception as e:
            print(f"Document ingestion failed: {e}")
            return False
    
    def get_document_stats(self) -> Dict:
        """Get statistics about processed documents"""
        try:
            # Count total documents
            doc_count_df = self.snowflake_client.execute_query(
                "SELECT COUNT(*) as total_docs FROM DOCUMENTS"
            )
            total_docs = doc_count_df.iloc[0]['TOTAL_DOCS'] if doc_count_df is not None else 0
            
            # Count total chunks
            chunk_count_df = self.snowflake_client.execute_query(
                "SELECT COUNT(*) as total_chunks FROM DOCUMENT_CHUNKS"
            )
            total_chunks = chunk_count_df.iloc[0]['TOTAL_CHUNKS'] if chunk_count_df is not None else 0
            
            # Get recent documents
            recent_docs_df = self.snowflake_client.execute_query(
                """SELECT FILENAME, UPLOAD_TIMESTAMP 
                   FROM DOCUMENTS 
                   ORDER BY UPLOAD_TIMESTAMP DESC 
                   LIMIT 5"""
            )
            
            recent_docs = recent_docs_df.to_dict('records') if recent_docs_df is not None else []
            
            return {
                "total_documents": total_docs,
                "total_chunks": total_chunks,
                "recent_documents": recent_docs
            }
            
        except Exception as e:
            print(f"Failed to get document stats: {e}")
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "recent_documents": []
            } 