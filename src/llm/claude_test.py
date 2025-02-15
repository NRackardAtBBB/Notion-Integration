from src.llm.handlers.anthropic_handler import AnthropicHandler
from src.llm.model_factory import ModelFactory
from config.settings import LLModel

# Test with a simple prompt
model_factory = ModelFactory()
llm = model_factory.create_model(LLModel.CLAUDE_SONNET)

def test_anthropic_handler():
    response = llm.process_input('Write a haiku about coding')
    print(response)
