# PDF Chatbot with AI Integration

A full-stack chatbot application that allows users to upload PDF documents and have intelligent conversations about their content using Groq's LLaMA model.

## Features

- **PDF Document Processing**: Upload and process PDF files for intelligent querying
- **AI-Powered Conversations**: Chat with documents using Groq's LLaMA 3.1 model
- **Session Management**: Persistent chat sessions with history
- **Personal Information Memory**: Remembers user details within sessions
- **Vector Search**: Advanced document retrieval using FAISS and sentence transformers
- **Real-time Chat**: Interactive web interface with real-time responses

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Groq API**: LLaMA 3.1-8b-instant model for AI responses
- **LangChain**: Document processing and vector operations
- **FAISS**: Vector similarity search
- **Sentence Transformers**: Text embeddings
- **PyPDF**: PDF text extraction

### Frontend
- **React**: User interface framework
- **Axios**: HTTP client for API communication
- **CSS**: Custom styling

## Prerequisites

- Python 3.8+
- Node.js 16+
- Groq API key

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd chatbot_Using_API_Key
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### 3. Configure Environment Variables
Edit `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Create environment file (optional)
cp .env.example .env
```

## Usage

### Start the Backend Server
```bash
cd backend
python main.py
```
Server runs on: `http://localhost:8000`

### Start the Frontend
```bash
cd frontend
npm start
```
Application runs on: `http://localhost:3000`

## API Endpoints

### Upload PDF
```http
POST /upload-pdf
Content-Type: multipart/form-data

Parameters:
- file: PDF file
- session_id: Optional session identifier
```

### Chat
```http
POST /chat
Content-Type: application/json

{
  "message": "Your question here",
  "session_id": "session-uuid"
}
```

### Get Chat History
```http
GET /chat-history/{session_id}
```

### Delete Session
```http
DELETE /session/{session_id}
```

### Health Check
```http
GET /health
```

## Project Structure

```
chatbot_Using_API_Key/
├── backend/
│   ├── data/
│   │   ├── sessions/          # Session storage
│   │   └── vectors/           # Vector embeddings
│   ├── logs/                  # Application logs
│   ├── uploads/               # Uploaded PDF files
│   ├── chat_handler.py        # AI conversation logic
│   ├── main.py               # FastAPI application
│   ├── pdf_processor.py      # PDF processing
│   ├── session_manager.py    # Session management
│   ├── persistent_storage.py # Data persistence
│   ├── logger.py             # Logging configuration
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Styling
│   │   └── index.js          # React entry point
│   └── package.json          # Node.js dependencies
└── README.md
```

## Features in Detail

### Document Processing
- Extracts text from PDF files
- Creates vector embeddings using sentence transformers
- Stores embeddings in FAISS index for fast retrieval

### AI Conversation Types
1. **Personal Questions**: Simple responses about user information
2. **Document Questions**: Detailed explanations based on uploaded PDFs
3. **General Questions**: Comprehensive answers on any topic

### Session Management
- Automatic session creation and management
- Persistent chat history storage
- Session cleanup for old conversations

## Configuration

### Response Length
The chatbot provides different response lengths based on question type:
- **Personal Info**: Short, simple answers
- **Document Questions**: Detailed 4-5 line explanations
- **General Questions**: Comprehensive responses

### Model Settings
- Model: `llama-3.1-8b-instant`
- Max Tokens: 800
- Temperature: 0.7

## Deployment

### Backend Deployment (Render)

1. **Create Render Account**
   - Sign up at [render.com](https://render.com)
   - Connect your GitHub repository

2. **Deploy Backend**
   - Create new "Web Service" on Render
   - Connect your repository
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add environment variable: `GROQ_API_KEY=your_groq_api_key`
   - Deploy from `backend` directory

### Frontend Deployment (Vercel)

1. **Create Vercel Account**
   - Sign up at [vercel.com](https://vercel.com)
   - Install Vercel CLI: `npm i -g vercel`

2. **Deploy Frontend**
   ```bash
   cd frontend
   vercel --prod
   ```
   - Set environment variable: `REACT_APP_API_BASE_URL=https://your-render-backend-url.onrender.com`
   - Or deploy via Vercel dashboard by connecting GitHub

3. **Environment Variables**
   - In Vercel dashboard, go to Project Settings > Environment Variables
   - Add: `REACT_APP_API_BASE_URL` with your Render backend URL

## Troubleshooting

### Common Issues

1. **Groq API Errors**
   - Verify API key in Render environment variables
   - Check API rate limits

2. **PDF Processing Fails**
   - Ensure PDF is not password protected
   - Check file size limits

3. **Frontend Connection Issues**
   - Verify backend URL in environment variables
   - Check CORS configuration
   - Ensure backend is deployed and running

4. **Deployment Issues**
   - Check build logs on Render/Vercel
   - Verify all environment variables are set
   - Ensure dependencies are correctly specified

### Logs
Check application logs in Render dashboard or `backend/logs/` for detailed error information.