import logging
from dotenv import load_dotenv

import os

from config.settings import MODEL_SETTINGS, MODEL_PROVIDERS
from config.prompts import SystemPrompts
import glob

class BaseModelHandler:
    def __init__(self, model_type=None, test_mode=False):
        self.logger = logging.getLogger('llm_logger').setLevel(logging.WARNING)
        load_dotenv()
        self.system_prompt = SystemPrompts.CONTENT_TAGGER.value

        self.model_type = model_type
        
        self.model_id = model_type.value
        self.provider = MODEL_PROVIDERS[self.model_id]
        self.model_settings = MODEL_SETTINGS[self.provider]
        self.context_window = self.model_settings['context_window']  
        self.test_mode = test_mode
     
    def _load_api_key(self, env_var_name):
        return os.getenv(env_var_name)

    def process_input(self, input_text: str) -> str:
            """Method to be implemented by child classes"""
            raise NotImplementedError
        
