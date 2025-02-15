import re
import tkinter as tk
from tkinter import filedialog
from docx import Document
from dataclasses import dataclass
from datetime import datetime
from typing import List
import os
import pathlib

import os
import tkinter as tk
from tkinter import filedialog
from docx import Document
import pathlib

def get_word_doc_text():
    file_path = r"C:\Users\nrackard\Code\Notion Integration\data\Text Library_BBBProfile--2020_TEAMS.docx"
    path = pathlib.Path(file_path)
    print(f"Opening file at: {path.absolute()}")
    doc = Document(str(path.absolute()))
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return "\n".join(full_text)



@dataclass
class TextChunk:
    project_name: str
    project_number: str
    title: str
    date_used: datetime
    tags: List[str]
    content: str

def parse_header(header_line: str) -> dict:
    """Parse header line into components"""
    # Remove < and > symbols
    header = header_line.strip('<>').strip()
    # Split by | and clean each component
    parts = [part.strip() for part in header.split('|')]
    
    # Handle date parsing with specific format
    if len(parts) < 4:
        print(parts)
    date_str = parts[3]
    if date_str == 'N/A' or date_str == '':
        date_used = None
    else:
        date_used = datetime.strptime(date_str, '%Y-%m-%d')
    
    return {
        'project_name': parts[0],
        'project_number': parts[1],
        'title': parts[2],
        'date_used': date_used,
        'tags': [tag.strip() for tag in parts[4].split(',')]
    }


def chunk_document(text: str) -> List[TextChunk]:
    """Split document into chunks based on headers"""
    # Break the text at ===BREAK===
    text = text.split('===BREAK===')[0]
    
    # Pattern to match headers
    header_pattern = r'<[^>]+>'
    
    # Split the document at headers
    chunks = re.split(header_pattern, text)
    headers = re.findall(header_pattern, text)
    
    # Remove empty chunks and strip whitespace
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    
    result = []
    for header, content in zip(headers, chunks):
        header_data = parse_header(header)
        chunk = TextChunk(
            project_name=header_data['project_name'],
            project_number=header_data['project_number'],
            title=header_data['title'],
            date_used=header_data['date_used'],
            tags=header_data['tags'],
            content=content
        )
        result.append(chunk)
    
    return result


if __name__ == "__main__":
    # Get text from Word doc
    doc_text = get_word_doc_text()
    
    # Parse into chunks
    chunks = chunk_document(doc_text)
    
    # Save to JSON
    import json
    from datetime import datetime
    
    # Custom JSON encoder to handle datetime
    class ChunkEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, TextChunk):
                return obj.__dict__
            return super().default(obj)
    
    with open("parsed_chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, cls=ChunkEncoder, indent=2)
