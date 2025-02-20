
import logging

from config.notion_config import NotionConfig
from src.clients.notion_wrapper import NotionWrapper
from src.parsers.text_parser import TextParser
import logging
from src.llm.claude_test import test_LLM
from src.clients.notion_setup import initialize_notion_databases
from config.settings import TEXT_LIBRARY_PATH
from src.parsers.excel_parser import ExcelParser
import argparse
from pathlib import Path


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def parse_excel():
    # Hardcoded paths using Path for cross-platform compatibility
    input_path = Path("data/raw/Boilerplates export_20250123_1208.xlsx")
    output_path = Path("data/processed/parsed_output.xlsx")
    test_rows = None  # Set to None for full file processing

    logging.info(f"Processing file: {input_path}")
    
    parser = ExcelParser(input_path)
    
    if test_rows:
        logging.info(f"Running in test mode with {test_rows} rows")
        df = parser.parse_text_column(test_rows=test_rows)
    else:
        logging.info("Processing entire file")
        df = parser.parse_text_column()
        
    parser.save_parsed_data(output_path, df)
    logging.info(f"Results saved to: {output_path}")


def main():

    setup_logging()
    parse_excel()

if __name__ == "__main__":
    setup_logging()
    parse_excel()


"""
def main():

    config = NotionConfig()
    notion = NotionWrapper(config.api_key, False)
    
    # Parse Document
    parser = TextParser(TEXT_LIBRARY_PATH)
    text_chunks = parser.parse_document()
    projects = parser.get_projects()

    project_table_id, text_table_id = initialize_notion_databases(notion, config)

    project_ids = notion.add_projects(project_table_id, projects)
    notion.add_text_chunks(text_table_id, text_chunks, project_ids)

if __name__ == "__main__":
    main()
"""