"""
This configuration file sets up various paths and configurations required for the Ideate Automation Tool.
It includes functionality to handle both local and network paths to ensure compatibility when running
scripts on different machines, including those with administrative privileges via Windows Task Scheduler.

The use of network paths (UNC paths) is necessary to handle scenarios where the script is executed with
elevated privileges, which may change the file access context, making mapped drive letters (e.g., N:)
unavailable. By providing both the mapped path and the UNC path, the script can dynamically determine
and use the correct path based on the execution environment.
"""

"""
This configuration file sets up various paths and configurations required for the Ideate Automation Tool.
It includes functionality to handle both local and network paths to ensure compatibility when running
scripts on different machines, including those with administrative privileges via Windows Task Scheduler.

The use of network paths (UNC paths) is necessary to handle scenarios where the script is executed with
elevated privileges, which may change the file access context, making mapped drive letters (e.g., N:)
unavailable. By providing both the mapped path and the UNC path, the script can dynamically determine
and use the correct path based on the execution environment.
"""

import os
from dotenv import load_dotenv
from datetime import datetime
from enum import Enum
from pathlib import Path

# Base directory for relative paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)


INPUT_WORD_DATA = PROJECT_ROOT / "data" / "raw" / "Text Library_BBBProfile--2020_TEAMS.docx"
INPUT_EXCEL_DATA = PROJECT_ROOT / "data" / "raw" / "Boilerplates export_20250123_1208.xlsx"

OUTPUT_EXCEL_DATA = PROJECT_ROOT / "data" / "processed" / "parsed_output.xlsx"



# Use environment variables with fallback to default values
input_path = Path("data/raw/Boilerplates export_20250123_1208.xlsx")
output_path = Path("data/processed/parsed_output.xlsx")

today_date = datetime.now()
today = today_date.strftime("%A")

# Load environment variables
load_dotenv()


# LLM Settings

MODEL_PROVIDERS = {
    'claude-3-5-sonnet-20241022' : 'anthropic',
    'claude-3-5-haiku-20241022' : 'anthropic',
    'claude-3-opus-20240229':'anthropic',

    'gpt-4o' : 'openai',
    'gpt-4o-mini' : 'openai',
    'o1-preview' : 'openai',
    'o1-mini' : 'openai',
    'o3-mini' : 'openai'
    }

MODEL_NAMES = {
    'claude-3-5-sonnet-20241022' : 'Claude Sonnet 3.5',
    'claude-3-5-haiku-20241022' : 'Claude Haiku 3.5',
    'claude-3-opus-20240229':'Claude Opus 3.0',

    'gpt-4o' : 'ChatGPT 4',
    'gpt-4o-mini' : 'ChatGPT 4-Mini',
    'o1-preview' : 'ChatGPT o1',
    'o1-mini' : 'ChatGPT o1-Mini',
    'o3-mini' : 'ChatGPT o3-Mini'
    }

MODEL_SETTINGS = {
    'anthropic': {
        'rate_limit': 5,
        'max_retries': 3,
        'batch_size': 500,
        'context_window' : 200000
    },
    'openai': {
        'rate_limit': 3,
        'max_retries': 5,
        'batch_size': 1000,
        'context_window' : 128000
    }
}

MODEL_IDS = {
    'claude_sonnet': 'claude-3-5-sonnet-20241022',
    'claude_haiku': 'claude-3-5-haiku-20241022',
    'claude_opus': 'claude-3-opus-20240229',
    '4o': 'gpt-4o',
    '4o_mini': 'gpt-4o-mini',
    'o1': 'o1-preview',
    'o1_mini': 'o1-mini',
    'o3_mini': 'o3-mini'
    }


PATH_SETTINGS = {
    'input_dir': 'inputs',
    'output_dir': 'output',
    'log_dir': 'logs'
}

PROCESSING_SETTINGS = {
    'chunk_size': 2000,
    'overlap': 200
}

DATABASE_SETTINGS = {
    'url': 'postgresql://user:password@localhost:5432/proposals_db',
    'pool_size': 5,
    'timeout': 30
}

ACCEPTS_SYSTEM_PROMPTS = [
        'gpt-4',
        'gpt-4-turbo-preview',
        'gpt-3.5-turbo'
    ]

class LLModel(Enum):
    CLAUDE_SONNET = 'claude-3-5-sonnet-20241022'
    CLAUDE_HAIKU = 'claude-3-5-haiku-20241022'
    CLAUDE_OPUS = 'claude-3-opus-20240229'

    GPT_4O = 'gpt-4o'
    GPT_4O_MINI =  'gpt-4o-mini'
    GPT_O1 = 'o1-preview'
    GPT_O1_MINI =  'o1-mini'
    GPT_O3_MINI = 'o3-mini'

    @property
    def id(self) -> str:
        return self.value
    
    @property
    def name(self) -> str:
        return MODEL_NAMES[self.value]

    @property
    def context_window(self) -> int:
        provider = MODEL_PROVIDERS[self.value]
        return MODEL_SETTINGS[provider]['context_window']
     
    @property
    def provider(self) -> str:
        return MODEL_PROVIDERS[self.value]
