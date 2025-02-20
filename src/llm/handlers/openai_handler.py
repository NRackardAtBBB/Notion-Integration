
from openai import OpenAI
from src.llm.handlers.base_handler import BaseModelHandler
import os
from config.settings import ACCEPTS_SYSTEM_PROMPTS

class OpenAIHandler(BaseModelHandler):
    def __init__(self, model_type='4o', test_mode=False):
        super().__init__(model_type, test_mode) 
        self.client = OpenAI(api_key=self._load_api_key('OPENAI_API_KEY'))

    def process_input(self, input_text: str) -> str:

        if self.model_type.id in ACCEPTS_SYSTEM_PROMPTS:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": input_text}
            ]
        else:
            input_text = self.system_prompt + " : " + input_text
            messages = [
                {"role": "user", "content": input_text}
            ]

        
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages
        )
        
        #self.logger.info(f"Processed input with system prompt: {self.system_prompt}")
        return response.choices[0].message.content
    
    def process_log_file(self, log_file_path: str = None) -> str:
        """
        Process input text and optional log file through the OpenAI API.
        
        Args:
            input_text (str): The primary input text to process
            log_file_path (str): Optional path to log file to include in context
            
        Returns:
            str: The model's response
        """
        # Combine input text with log contents if provided
        combined_input = self.combine_input_with_logs(log_file_path)

        response = self.client.chat.completions.create(
            model=self.model_type.id,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": combined_input}
            ]
        )
        
        return response.choices[0].message.content


