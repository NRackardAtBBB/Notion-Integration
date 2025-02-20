from config.notion_config import NotionConfig, DBTables
from src.models.models import Project, TextChunk

def initialize_notion_databases(notion_client, config):
    """Initialize or get Notion databases for projects and text library"""
    projects_id = notion_client.search_database("BBB Projects")
    text_library_id = notion_client.search_database("BBB Text Library")
    
    if not projects_id:
        projects_id = notion_client.create_database(
            config.page_id,
            DBTables.PROJECTS.value,
            Project.database_schema()
        )

    if not text_library_id:
        text_library_id = notion_client.create_database(
            config.page_id, 
            DBTables.TEXT_LIBRARY.value, 
            TextChunk.database_schema(projects_id)
        )
        
    return projects_id, text_library_id
