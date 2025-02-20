
import logging

from config.notion_config import NotionConfig
from src.clients.notion_wrapper import NotionWrapper
from src.parsers.text_parser import TextParser
import logging
from src.clients.notion_setup import initialize_notion_databases
from config.settings import INPUT_WORD_DATA
from src.parsers.excel_parser import parse_excel


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def main():
    # Parse Document
    parser = TextParser(INPUT_WORD_DATA)
    
    # Uncomment to parse excel file to formatted excel file
    #parse_excel()
    
    # Parse word document and extract text chunks and projects
    text_chunks = parser.parse_document()
    projects = parser.get_projects()

    # Initialize Notion
    config = NotionConfig()
    notion = NotionWrapper(config.api_key, False)

    project_table_id, text_table_id = initialize_notion_databases(notion, config)

    # Add projects and text chunks to Notion
    project_ids = notion.add_projects(project_table_id, projects)
    notion.add_text_chunks(text_table_id, text_chunks, project_ids)

if __name__ == "__main__":
    main()


