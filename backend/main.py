from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import os
import asyncio
from contextlib import asynccontextmanager
from pdf_processor import PDFProcessor
import session_manager
from chat_handler import ChatHandler
from logger import main_logger

pdf_processor = None
chat_handler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pdf_processor, chat_handler
    pdf_processor = PDFProcessor()
    chat_handler = ChatHandler()
    
    asyncio.create_task(periodic_cleanup())
    main_logger.info("Server started with Groq API")
    
    yield
    
    main_logger.info("Server shutting down")

async def periodic_cleanup():
    while True:
        await asyncio.sleep(86400)
        try:
            session_manager.cleanup_old_sessions()
            main_logger.info("Cleanup completed")
        except Exception as e:
            main_logger.error(f"Cleanup error: {e}")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), session_id: str = Form(None)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files allowed")
    
    session_id = session_id or str(uuid.uuid4())
    file_path = f"uploads/{session_id}_{file.filename}"
    
    try:
        os.makedirs("uploads", exist_ok=True)
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        vector_store = pdf_processor.process_pdf(file_path)
        session = session_manager.update_session_with_pdf(session_id, vector_store, file.filename)
        
        main_logger.info(f"PDF processed: {file.filename}")
        return {"session_id": session_id, "filename": session.get("filename", file.filename)}
    
    except Exception as e:
        main_logger.error(f"PDF error: {e}")
        raise HTTPException(500, f"Error: {str(e)}")

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    try:
        if not session_manager.get_session(chat_message.session_id):
            session_manager.create_session(chat_message.session_id, None, "General Chat")
        
        response = chat_handler.handle_message(chat_message.message, chat_message.session_id)
        return ChatResponse(response=response, session_id=chat_message.session_id)
    
    except Exception as e:
        main_logger.error(f"Chat error: {e}")
        raise HTTPException(500, str(e))

@app.get("/chat-history/{session_id}")
async def get_chat_history(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    
    return {
        "history": session.get("chat_history", []),
        "filename": session.get("filename", ""),
        "has_vector_store": bool(session.get("vector_store"))
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Server running with Groq API"}

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    try:
        session_manager.delete_session(session_id)
        return {"message": "Session deleted"}
    except Exception as e:
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)