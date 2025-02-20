import logging
from dotenv import load_dotenv

import os

from config.settings import MODEL_SETTINGS, MODEL_PROVIDERS
from config.prompts import SystemPrompts

from config.prompts import generate_tagging_prompt
from src.utils.tag_repository import load_approved_tags, update_approved_tags

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
    
    def process_tags(self, input_text):   
        # Get tagging-specific prompt
        approved_tags = load_approved_tags()
        tagging_prompt = generate_tagging_prompt(approved_tags=approved_tags)

        message_with_prompt = tagging_prompt + "\n" + input_text
        
        output = self.process_input(message_with_prompt)
        print(output)
   
        # Extract selected tags
        selected_tags = []
        if '<selected_tags>' in output and '</selected_tags>' in output:
            selected_part = output.split('<selected_tags>')[1].split('</selected_tags>')[0].strip()
            selected_tags = [tag.strip() for tag in selected_part.split('\n') if tag.strip()]

        # Extract suggested tags
        suggested_tags = []
        if '<suggested_new_tags>' in output and '</suggested_new_tags>' in output:
            suggested_part = output.split('<suggested_new_tags>')[1].split('</suggested_new_tags>')[0].strip()
            suggested_tags = [tag.strip() for tag in suggested_part.split('\n') if tag.strip()]
            
        update_approved_tags(suggested_tags)
        
        return selected_tags + suggested_tags
        
