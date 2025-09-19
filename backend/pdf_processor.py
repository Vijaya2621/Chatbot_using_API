import os
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

class PDFProcessor:
    def process_pdf(self, file_path: str):
        try:
            # Extract text from PDF
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            if not text.strip():
                raise ValueError("No content found in PDF")
            
            # Clean up uploaded file
            os.remove(file_path)
            return text
            
        except Exception as e:
            # Clean up file on error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e