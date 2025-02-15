
from anthropic import Anthropic
from src.llm.handlers.base_handler import BaseModelHandler
from config.prompts import generate_tagging_prompt
from src.utils.tag_repository import load_approved_tags, update_approved_tags

class AnthropicHandler(BaseModelHandler):

    def __init__(self, model_type='claude3_5_haiku', test_mode=False):
        super().__init__(model_type, test_mode)
        self.client = Anthropic(api_key=self._load_api_key('ANTHROPIC_API_KEY'))

    def process_input(self, input_text):
        messages = [{"role": "user", "content": input_text}]
        response = self.client.messages.create(
            model=self.model_id,
            system=self.system_prompt,
            messages=messages,
            max_tokens=8192
        )

        return response.content[0].text
    
    def process_tags(self, input_text):
        approved_tags = load_approved_tags()
        tagging_prompt = generate_tagging_prompt(approved_tags=approved_tags)

        messages = [{"role": "user", "content": input_text}]
        response = self.client.messages.create(
            model=self.model_id,
            system=tagging_prompt,
            messages=messages,
            max_tokens=8192
        )

        output = response.content[0].text

        if '<selected_tags>' in output and '</selected_tags>' in output:
            selected_part = output.split('<selected_tags>')[1].split('</selected_tags>')[0].strip()
            selected_tags = [tag.strip() for tag in selected_part.split('\n') if tag.strip()]

        # Extract suggested tags if they exist
        suggested_tags = []
        if '<suggested_new_tags>' in output and '</suggested_new_tags>' in output:
            suggested_part = output.split('<suggested_new_tags>')[1].split('</suggested_new_tags>')[0].strip()
            suggested_tags = [tag.strip() for tag in suggested_part.split('\n') if tag.strip()]
            
        update_approved_tags(suggested_tags)

        merged_tags = selected_tags + suggested_tags
        
        return merged_tags
