from typing import List, Dict, Any, Tuple
import re
from datetime import datetime
from docx import Document
from src.models.models import TextChunk, Project
from src.utils.tags_sanitizer import sanitize_tags
from src.utils.tag_repository import update_approved_tags
from src.llm.model_factory import ModelFactory
from config.settings import LLModel
import logging

# Test with a simple prompt
model_factory = ModelFactory()
llm = model_factory.create_model(LLModel.GPT_O1_MINI)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class TextParser:
    def __init__(self, file_path: str, add_ai_tags: bool = False):
        self.file_path = file_path
        self.projects: Dict[str, Project] = {}  # Key: project_number
        self.add_ai_tags = add_ai_tags

    def get_word_doc_text(self) -> str:
        doc = Document(self.file_path)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        return "\n".join(full_text)
    
    def parse_header(self, header_line: str) -> Tuple[Project, dict]:
        # Remove < and > symbols and split components
        header = header_line.strip('<>').strip()
        parts = [part.strip() for part in header.split('|')]

        # Validate header has correct number of parts
        expected_parts = 5
        if len(parts) != 5:
            logging.error(f"Invalid header format. Expected 5 parts, got {len(parts)}")
            logging.error(f"Header content: {header_line}")
            raise ValueError(f"Header must contain {expected_parts} parts separated by '|'")
    
        
        # Create project from header
        project = Project(
            name=parts[0],
            project_number=parts[1]
        )
        
        # Parse chunk metadata
        chunk_data = {
            'title': parts[2],
            'date': datetime.strptime(parts[3], '%Y-%m-%d') if parts[3] not in ['N/A', ''] else None,
            'tags': [tag.strip() for tag in parts[4].split(',')] if len(parts) > 4 else None
        }
        
        return project, chunk_data
    
    def parse_document(self) -> List[TextChunk]:
        raw_text = self.get_word_doc_text()
        
        # Split at BREAK
        text = raw_text.split('===BREAK===')[0]
        
        # Find headers and content
        header_pattern = r'<[^>]+>'
        chunks = re.split(header_pattern, text)
        headers = re.findall(header_pattern, text)
        
        # Clean chunks
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        
        text_chunks = []
        for header, content in zip(headers, chunks):
            project, chunk_data = self.parse_header(header)
            
            # Store unique projects
            if project.project_number not in self.projects:
                self.projects[project.project_number] = project
            
            # Get raw tags from header
            raw_tags = chunk_data['tags']
            # Sanitize tags using fuzzy matching to consolidate similar ones
            sanitized_tags = sanitize_tags(raw_tags)
            # Update the approved tags repository with any new sanitized tags
            update_approved_tags(sanitized_tags)

            # Generate AI tags if enabled
            if self.add_ai_tags:
                ai_tags = llm.process_tags(content)
            else:
                ai_tags = []
            
            # Create text chunk with the sanitized tags
            chunk = TextChunk(
                content=content,
                title=chunk_data['title'],
                project_number=project.project_number,
                date=chunk_data['date'],
                tags=chunk_data['tags'],
                ai_tags=ai_tags
            )

            text_chunks.append(chunk)
        
        return text_chunks

    def get_projects(self) -> List[Project]:
        return list(self.projects.values())

    def generate_tags_from_content(self, content: str) -> List[str]:
        """
        Analyzes content and returns relevant tags.
        This is a placeholder for more sophisticated tag generation logic.
        """
        # Placeholder logic - can be enhanced with NLP, keyword extraction, etc.
        base_tags = []
        
        # Example simple tag rules
        if len(content) > 1000:
            base_tags.append("long-form")
        if "technical" in content.lower():
            base_tags.append("technical")
        if "scope" in content.lower():
            base_tags.append("scope")
            
        return base_tags