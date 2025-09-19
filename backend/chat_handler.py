import os
import re
from groq import Groq
import session_manager
from logger import chat_logger
from dotenv import load_dotenv

load_dotenv()

class ChatHandler:
    def __init__(self):
        self.client = Groq()
        self.model = "llama-3.1-8b-instant"
        self._personal_keywords = {
            "my name", "what is my", "who am i", "remember", "i told you",
            "what did i say", "do you know my", "about me", "my age",
            "my job", "my work", "my hobby", "my favorite", "where do i"
        }
        self._doc_keywords = {
            "document", "pdf", "file", "text", "according to", "based on",
            "in the document", "what does it say", "from the file", "provided",
            "paper says", "assignment", "students should"
        }
    
    def handle_message(self, message: str, session_id: str) -> str:
        message = message.strip()
        if not message:
            return "Please enter a valid question or message."
        if len(message) < 2:
            return "Please enter a more detailed question."
        
        session = session_manager.get_session(session_id)
        if not session:
            session = session_manager.create_session(session_id, None, "General Chat")
        
        session_manager.add_message(session_id, "user", message)
        
        if self._is_personal_question(message):
            response = self._handle_personal_question(message, session)
        elif session.get("pdf_text") and self._is_document_question(message):
            response = self._handle_document_question(message, session)
        else:
            response = self._handle_general_question(message)
        
        session_manager.add_message(session_id, "assistant", response)
        return response
    
    def _is_personal_question(self, message: str) -> bool:
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self._personal_keywords)
    
    def _is_document_question(self, message: str) -> bool:
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self._doc_keywords)
    
    def _call_groq(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                max_tokens=800,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            chat_logger.error(f"Groq error: {e}")
            return "I'm having trouble responding right now. This could be due to a temporary connection issue or high server load. Please try asking your question again in a moment, and I'll do my best to provide you with a helpful and detailed response."
    
    def _handle_personal_question(self, message: str, session: dict) -> str:
        message_lower = message.lower()
        chat_history = session.get("chat_history", [])
        
        if "name" in message_lower:
            for msg in reversed(chat_history):
                if msg["role"] == "user":
                    content = msg["content"].lower()
                    if "my name is" in content:
                        name = content.split("my name is")[1].strip().split()[:3]
                        return f"Your name is {' '.join(name)}."
            return "I don't know your name yet. Please tell me!"
        
        elif "age" in message_lower:
            for msg in reversed(chat_history):
                if msg["role"] == "user" and "years old" in msg["content"].lower():
                    age_match = re.search(r'(\d+)\s*years?\s*old', msg["content"].lower())
                    if age_match:
                        return f"You are {age_match.group(1)} years old."
            return "I don't know your age. Please tell me!"
        
        relevant_info = [
            msg["content"] for msg in reversed(chat_history[-50:])
            if msg["role"] == "user" and any(word in msg["content"].lower() 
                for word in ["my", "i am", "i work", "i like"])
        ]
        
        if relevant_info:
            context = "\n".join(relevant_info[:5])
            prompt = f"Personal info: {context}\nQuestion: {message}\nAnswer briefly:"
            return self._call_groq(prompt)
        
        return "I don't have that information about you yet."
    
    def _handle_document_question(self, message: str, session: dict) -> str:
        try:
            pdf_text = session.get("pdf_text", "")
            if pdf_text:
                # Use first 2000 characters to stay within token limits
                context = pdf_text[:2000]
                filename = session.get("filename", "documents")
                prompt = (
                    f"You are a knowledgeable AI assistant helping users understand documents. Based on the context provided from {filename}, give a detailed and comprehensive explanation. Provide 4-5 lines of explanation, include relevant details, examples, and context to help the user fully understand the topic.\n\n"
                    f"Context from {filename}:\n{context}\n\n"
                    f"Question: {message}\n\n"
                    "Provide a thorough, well-explained answer based on the context above. Include specific details and elaborate on key points:"
                )
                return self._call_groq(prompt)
            
            return "I couldn't find relevant information in the documents."
        
        except Exception as e:
            chat_logger.error(f"Document search error: {e}")
            return "I couldn't search the documents. Please try again."
    
    def _handle_general_question(self, message: str) -> str:
        prompt = f"You are a helpful and knowledgeable AI assistant. Provide detailed, informative responses that are 4-5 lines long when appropriate. Explain concepts clearly, provide context, and give comprehensive answers that help users understand the topic fully.\n\nUser: {message}\n\nProvide a detailed and helpful response:"
        return self._call_groq(prompt)