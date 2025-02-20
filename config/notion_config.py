import os
from dotenv import load_dotenv
from enum import Enum



class NotionConfig:
    class DBTables(Enum):
        PROJECTS = 'Projects'
        TEXT_LIBRARY = 'Text Library'

    def __init__(self):
        load_dotenv()
        self.api_key = self._get_env_var('NOTION_API_KEY')
        self.page_id = self._get_env_var('NOTION_PAGE_ID')

    def _get_env_var(self, var_name: str) -> str:
        value = os.getenv(var_name)
        if not value:
            raise EnvironmentError(f"Missing required environment variable: {var_name}")
        return value
