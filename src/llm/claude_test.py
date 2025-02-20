from src.llm.handlers.anthropic_handler import AnthropicHandler
from src.llm.model_factory import ModelFactory
from config.settings import LLModel 

# Test with a simple prompt
model_factory = ModelFactory()
llm = model_factory.create_model(LLModel.GPT_O1_MINI)

def test_LLM(input = "Write a haiku about coding"):
    response = llm.process_input(input)
    print(response)
