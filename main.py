
import logging

from src.models.models import Project, TextChunk
from config.notion_config import NotionConfig, DBTables
from src.clients.notion_wrapper import NotionWrapper
from src.parsers.text_parser import TextParser
import logging
from src.llm.claude_test import test_anthropic_handler

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def main():

    config = NotionConfig()
    notion = NotionWrapper(config.api_key, False)
    
    # Parse Document
    file_path = "data/raw/Text Library_BBBProfile--2020_TEAMS.docx"
    parser = TextParser(file_path)
    text_chunks = parser.parse_document()
    projects = parser.get_projects()

    # Create or get databases
    
    projects_id = notion.search_database("BBB Projects")
    
    if not projects_id:
        projects_id = notion.create_database(
            config.page_id,
            DBTables.PROJECTS.value,
            Project.database_schema()
            )
    text_library_id = notion.search_database("BBB Text Library")

    if not text_library_id:
        text_library_id = notion.create_database(
            config.page_id, 
            DBTables.TEXT_LIBRARY.value, 
            TextChunk.database_schema(projects_id)
            )
    
    # Add projects to Notion
    project_ids = {}
    for project in projects:
        response = notion.create_page(projects_id, project.to_notion_properties())
        project_ids[project.project_number] = response["id"]
        logging.info(f"Added project: {project.name}")

    # Add text chunks with project relations
    for chunk in text_chunks:
        notion_uuid = project_ids[chunk.project_number]
        chunk.project_id = notion_uuid
        notion.create_page(text_library_id, chunk.to_notion_properties())
        logging.info(f"Added chunk: {chunk.title}")

if __name__ == "__main__":
    main()
