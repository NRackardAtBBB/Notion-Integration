# from ..llm.handlers.openai_handler import OpenAIHandler
from ..llm.handlers.anthropic_handler import AnthropicHandler
from config.prompts import SystemPrompts
from typing import Dict
from config.settings import LLModel


class ModelFactory:
    @staticmethod
    def create_model(model_type: LLModel, test_mode: bool = False):

        model_handlers = {
            "anthropic": AnthropicHandler,
            #"openai": OpenAIHandler
        }

        handler_class = model_handlers.get(model_type.provider)
        
        if handler_class:
            return handler_class(
                model_type=model_type,
                test_mode=test_mode
            )
            
        # Default fallback with standard configuration
        return AnthropicHandler(model_type=model_type)