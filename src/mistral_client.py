import openai
import time
from typing import List, Dict, Optional
from src.config import Config

class MistralClient:
    """Client for Mistral LLM API interactions"""
    
    def __init__(self):
        # Configure OpenAI client to use Mistral endpoint
        self.client = openai.OpenAI(
            api_key=Config.MISTRAL_API_KEY,
            base_url="https://api.mistral.ai/v1"
        )
        self.model = "mistral-large-latest"  # Default model
    
    def generate_response(self, 
                         user_question: str, 
                         context_documents: List[Dict], 
                         chat_history: List[Dict] = None) -> str:
        """Generate response using Mistral LLM with retrieved context"""
        
        # Prepare context from retrieved documents
        context = self._format_context(context_documents)
        
        # Prepare conversation history
        messages = self._prepare_messages(user_question, context, chat_history)
        
        return self._make_api_call_with_retry(
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=1000
            ),
            "generate response"
        )
    
    def _make_api_call_with_retry(self, api_call_func, operation_name: str, max_retries: int = 3) -> str:
        """Make API call with retry logic for rate limiting"""
        for attempt in range(max_retries):
            try:
                response = api_call_func()
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                error_str = str(e)
                
                # Handle rate limiting
                if "429" in error_str or "service_tier_capacity_exceeded" in error_str:
                    wait_time = (2 ** attempt) * 5  # Exponential backoff: 5, 10, 20 seconds
                    print(f"⚠️ Rate limit hit during {operation_name}. Waiting {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                    
                    if attempt < max_retries - 1:  # Don't wait on the last attempt
                        time.sleep(wait_time)
                        continue
                    else:
                        return f"I apologize, but I'm currently experiencing high demand. Please try asking your question again in a few minutes."
                
                # Handle other errors
                print(f"Mistral API error during {operation_name}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Brief wait for other errors
                    continue
                else:
                    return "I apologize, but I'm having trouble generating a response right now. Please try again."
        
        return "Service temporarily unavailable. Please try again later."
    
    def _format_context(self, documents: List[Dict]) -> str:
        """Format retrieved documents into context string"""
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            chunk_text = doc.get('CHUNK_TEXT', '')
            filename = doc.get('FILENAME', 'Unknown')
            
            context_parts.append(f"Document {i} (from {filename}):\n{chunk_text}")
        
        return "\n\n".join(context_parts)
    
    def _prepare_messages(self, 
                         user_question: str, 
                         context: str, 
                         chat_history: List[Dict] = None) -> List[Dict]:
        """Prepare messages for the Mistral API"""
        
        system_prompt = """You are a helpful AI assistant that answers questions based on the provided document context. 

Instructions:
1. Use ONLY the information provided in the context documents to answer questions
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Cite specific documents when referencing information
4. Be concise but thorough in your responses
5. If asked about something not in the context, politely explain that you can only answer based on the provided documents

Context Documents:
{context}"""

        messages = [
            {
                "role": "system",
                "content": system_prompt.format(context=context)
            }
        ]
        
        # Add chat history if available
        if chat_history:
            for chat in reversed(chat_history[-5:]):  # Last 5 exchanges
                messages.append({
                    "role": "user",
                    "content": chat.get('USER_QUESTION', '')
                })
                messages.append({
                    "role": "assistant",
                    "content": chat.get('BOT_RESPONSE', '')
                })
        
        # Add current user question
        messages.append({
            "role": "user",
            "content": user_question
        })
        
        return messages
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate a summary of the given text"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"Summarize the following text in {max_length} characters or less. Be concise and capture the key points."
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Summary generation error: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text
    
    def generate_follow_up_questions(self, 
                                   user_question: str, 
                                   bot_response: str, 
                                   context_documents: List[Dict]) -> List[str]:
        """Generate follow-up questions based on the conversation"""
        try:
            context = self._format_context(context_documents)
            
            messages = [
                {
                    "role": "system",
                    "content": """Based on the user's question, bot's response, and available context, generate 3 relevant follow-up questions that the user might want to ask. Make the questions specific and actionable."""
                },
                {
                    "role": "user",
                    "content": f"""
User Question: {user_question}
Bot Response: {bot_response}
Available Context: {context[:1000]}...

Generate 3 follow-up questions:"""
                }
            ]
            
            # Use retry logic for follow-up questions with shorter max_tokens
            response_text = self._make_api_call_with_retry(
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=200
                ),
                "follow-up questions",
                max_retries=2  # Fewer retries for non-critical feature
            )
            
            # Parse the response to extract questions
            questions = []
            
            for line in response_text.split('\n'):
                line = line.strip()
                if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('-')):
                    # Clean up the question
                    question = line.split('.', 1)[-1].strip() if '.' in line else line.strip('- ')
                    if question:
                        questions.append(question)
            
            return questions[:3]  # Return max 3 questions
            
        except Exception as e:
            print(f"Follow-up question generation error: {e}")
            return [] 