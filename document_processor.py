import fitz  # PyMuPDF
from docx import Document
import tempfile
import os

def process_pdf(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_file_path = tmp_file.name

    doc = fitz.open(tmp_file_path)
    texts = []
    
    for page in doc:
        texts.append(page.get_text())
    
    doc.close()
    os.unlink(tmp_file_path)
    return texts

def process_docx(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_file_path = tmp_file.name

    doc = Document(tmp_file_path)
    texts = []
    
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            texts.append(paragraph.text)
    
    os.unlink(tmp_file_path)
    return texts

def process_txt(file):
    content = file.getvalue().decode("utf-8")
    return [content]

def process_documents(files):
    all_texts = []
    
    for file in files:
        if file.name.endswith('.pdf'):
            texts = process_pdf(file)
        elif file.name.endswith('.docx'):
            texts = process_docx(file)
        elif file.name.endswith('.txt'):
            texts = process_txt(file)
        else:
            continue
            
        all_texts.extend(texts)
    
    return all_texts