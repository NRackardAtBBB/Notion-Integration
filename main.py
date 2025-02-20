
"""
Notion Integration Application

This script processes text documents and uploads their content to Notion databases.
It handles parsing documents, extracting projects and text chunks, and creating 
corresponding entries in Notion.
"""

import logging
from config.notion_config import NotionConfig
from src.clients.notion_wrapper import NotionWrapper
from src.clients.notion_setup import initialize_notion_databases

from src.parsers.text_parser import TextParser
from config.settings import INPUT_WORD_DATA
from src.parsers.excel_parser import parse_excel


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def main():

    # Functionality in progress - Uncomment to parse excel file to formatted excel file
    #parse_excel()

    # Parse word document and extract text chunks and projects
    parser = TextParser(INPUT_WORD_DATA)
    text_chunks = parser.parse_document()
    projects = parser.get_projects()

    # Initialize Notion client
    notion = NotionWrapper(test_mode=False)

    # Add projects and text chunks to Notion
    project_ids = notion.add_projects(projects)
    notion.add_text_chunks(text_chunks, project_ids)

if __name__ == "__main__":
    main()


