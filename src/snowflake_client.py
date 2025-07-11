import snowflake.connector
import pandas as pd
from typing import List, Dict, Any, Optional
import json
from src.config import Config

class SnowflakeClient:
    """Client for Snowflake database operations"""
    
    def __init__(self):
        self.connection_params = Config.get_snowflake_connection_params()
        self.connection = None
    
    def connect(self) -> bool:
        """Establish connection to Snowflake"""
        try:
            self.connection = snowflake.connector.connect(**self.connection_params)
            return True
        except Exception as e:
            print(f"Failed to connect to Snowflake: {e}")
            return False
    
    def disconnect(self):
        """Close Snowflake connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Optional[pd.DataFrame]:
        """Execute a query and return results as DataFrame"""
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Fetch results if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return pd.DataFrame(results, columns=columns)
            else:
                self.connection.commit()
                return None
                
        except Exception as e:
            print(f"Query execution failed: {e}")
            return None
        finally:
            cursor.close()
    
    def insert_document(self, filename: str, content: str, metadata: Dict = None) -> Optional[int]:
        """Insert a document into the database"""
        # For now, skip metadata to get core functionality working
        query = """
        INSERT INTO DOCUMENTS (FILENAME, CONTENT)
        VALUES (%s, %s)
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (filename, content))
            
            # Get the inserted document ID using Snowflake method
            cursor.execute("SELECT MAX(ID) FROM DOCUMENTS WHERE FILENAME = %s", (filename,))
            result = cursor.fetchone()
            doc_id = result[0] if result else None
            
            self.connection.commit()
            print(f"✅ Document inserted successfully with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            print(f"Failed to insert document: {e}")
            return None
        finally:
            cursor.close()
    
    def insert_document_chunks(self, chunks: List[Dict]) -> bool:
        """Insert document chunks into the database"""
        if not chunks:
            return True
            
        # For now, skip metadata to get core functionality working
        query = """
        INSERT INTO DOCUMENT_CHUNKS (DOCUMENT_ID, CHUNK_TEXT, CHUNK_INDEX)
        VALUES (%s, %s, %s)
        """
            
        try:
            cursor = self.connection.cursor()
            
            for chunk in chunks:
                cursor.execute(query, (
                    chunk['document_id'],
                    chunk['text'],
                    chunk['index']
                ))
            
            self.connection.commit()
            print(f"✅ Inserted {len(chunks)} document chunks successfully")
            return True
            
        except Exception as e:
            print(f"Failed to insert document chunks: {e}")
            return False
        finally:
            cursor.close()
    
    def search_documents_cortex(self, query: str, limit: int = 5) -> List[Dict]:
        """Search documents using Cortex Search with fallback to text search"""
        # First try Cortex Search
        cortex_query = f"""
        SELECT 
            dc.CHUNK_TEXT,
            dc.CHUNK_METADATA,
            d.FILENAME,
            d.METADATA as DOC_METADATA
        FROM TABLE(CORTEX_SEARCH(
            'DOCUMENT_SEARCH_SERVICE',
            '{query}',
            {limit}
        )) cs
        JOIN DOCUMENT_CHUNKS dc ON cs.ID = dc.ID
        JOIN DOCUMENTS d ON dc.DOCUMENT_ID = d.ID
        """
        
        try:
            results_df = self.execute_query(cortex_query)
            if results_df is not None and not results_df.empty:
                return results_df.to_dict('records')
        except Exception as e:
            print(f"Cortex search failed, falling back to text search: {e}")
        
        # Fallback to simple text search
        return self.search_documents_fallback(query, limit)
    
    def search_documents_fallback(self, query: str, limit: int = 5) -> List[Dict]:
        """Fallback search using simple text matching"""
        # First, let's try a simple query to see what we have
        simple_query = """
        SELECT 
            dc.CHUNK_TEXT,
            d.FILENAME,
            dc.CHUNK_INDEX,
            d.ID as DOC_ID
        FROM DOCUMENT_CHUNKS dc
        JOIN DOCUMENTS d ON dc.DOCUMENT_ID = d.ID
        ORDER BY d.ID DESC
        LIMIT 10
        """
        
        try:
            # First check if we have any documents at all
            test_results = self.execute_query(simple_query)
            if test_results is not None and not test_results.empty:
                print(f"📊 Database contains {len(test_results)} document chunks")
                
                # Now try the actual search
                search_query = f"""
                SELECT 
                    dc.CHUNK_TEXT,
                    d.FILENAME,
                    dc.CHUNK_INDEX,
                    '' as CHUNK_METADATA,
                    '' as DOC_METADATA
                FROM DOCUMENT_CHUNKS dc
                JOIN DOCUMENTS d ON dc.DOCUMENT_ID = d.ID
                WHERE UPPER(dc.CHUNK_TEXT) LIKE UPPER('%{query}%')
                   OR UPPER(d.FILENAME) LIKE UPPER('%{query}%')
                   OR UPPER(d.CONTENT) LIKE UPPER('%{query}%')
                ORDER BY d.ID DESC
                LIMIT {limit}
                """
                
                results_df = self.execute_query(search_query)
                if results_df is not None and not results_df.empty:
                    print(f"✅ Found {len(results_df)} documents using text search")
                    return results_df.to_dict('records')
                else:
                    print(f"❌ No documents found for query: '{query}' but database has {len(test_results)} chunks")
                    # Return some sample documents to help with debugging
                    return test_results.head(3).to_dict('records')
            else:
                print("❌ No documents found in database at all")
                return []
                
        except Exception as e:
            print(f"Fallback search failed: {e}")
            # Try even simpler query
            try:
                count_query = "SELECT COUNT(*) as total FROM DOCUMENT_CHUNKS"
                count_result = self.execute_query(count_query)
                if count_result is not None:
                    total = count_result.iloc[0]['TOTAL']
                    print(f"📊 Database contains {total} total chunks")
            except:
                pass
            return []
    
    def save_chat_history(self, session_id: str, question: str, response: str, 
                         retrieved_docs: List[Dict] = None) -> bool:
        """Save chat interaction to history"""
        # For now, skip retrieved_docs metadata to get core functionality working
        query = """
        INSERT INTO CHAT_HISTORY (SESSION_ID, USER_QUESTION, BOT_RESPONSE)
        VALUES (%s, %s, %s)
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (session_id, question, response))
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"Failed to save chat history: {e}")
            return False
        finally:
            cursor.close()
    
    def get_chat_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve chat history for a session"""
        query = """
        SELECT USER_QUESTION, BOT_RESPONSE, TIMESTAMP
        FROM CHAT_HISTORY
        WHERE SESSION_ID = %s
        ORDER BY TIMESTAMP DESC
        LIMIT %s
        """
        
        try:
            results_df = self.execute_query(query, (session_id, limit))
            if results_df is not None and not results_df.empty:
                return results_df.to_dict('records')
            return []
        except Exception as e:
            print(f"Failed to retrieve chat history: {e}")
            return [] 