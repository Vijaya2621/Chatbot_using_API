from persistent_storage import PersistentStorage
import time
import os
import shutil
from typing import Optional, Dict, Any

storage = PersistentStorage()
active_sessions: Dict[str, Dict[str, Any]] = {}

def create_session(session_id: str, vector_store, filename: str) -> Dict[str, Any]:
    session_data = {
        "session_id": session_id,
        "vector_store": vector_store,
        "filename": filename or "General Chat",
        "chat_history": [],
        "created_at": time.time(),
        "last_activity": time.time()
    }
    
    active_sessions[session_id] = session_data
    storage.save_session(session_id, session_data)
    
    return session_data

def update_session_with_pdf(session_id: str, vector_store, filename: str) -> Dict[str, Any]:
    session = get_session(session_id)
    
    if session:
        session["vector_store"] = vector_store
        
        old_filename = session.get("filename", "")
        if old_filename and old_filename != "General Chat":
            existing_files = {f.strip() for f in old_filename.split(",")}
            if filename not in existing_files:
                existing_files.add(filename)
                session["filename"] = ", ".join(sorted(existing_files))
        else:
            session["filename"] = filename
            
        session["last_activity"] = time.time()
        active_sessions[session_id] = session
        storage.save_session(session_id, session)
        return session
    
    return create_session(session_id, vector_store, filename)

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    if session_id in active_sessions:
        return active_sessions[session_id]
    
    session_data = storage.load_session(session_id)
    if session_data:
        active_sessions[session_id] = session_data
        return session_data
    
    return None

def add_message(session_id: str, role: str, content: str) -> None:
    session = get_session(session_id)
    if session:
        session["chat_history"].append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        session["last_activity"] = time.time()
        
        if len(session["chat_history"]) > 100:
            session["chat_history"] = session["chat_history"][-100:]
        
        active_sessions[session_id] = session
        storage.save_session(session_id, session)

def delete_session(session_id: str) -> None:
    active_sessions.pop(session_id, None)
    
    session_file = f"{storage.storage_dir}/sessions/{session_id}.json"
    if os.path.exists(session_file):
        os.remove(session_file)
    
    vector_path = f"{storage.storage_dir}/vectors/{session_id}"
    if os.path.exists(vector_path):
        shutil.rmtree(vector_path)

def cleanup_old_sessions(max_age_days: int = 7) -> None:
    storage.cleanup_old_sessions(max_age_days)
    
    current_time = time.time()
    max_age_seconds = max_age_days * 86400
    
    expired_sessions = [
        sid for sid, session in active_sessions.items()
        if current_time - session.get("last_activity", 0) > max_age_seconds
    ]
    
    for sid in expired_sessions:
        active_sessions.pop(sid, None)