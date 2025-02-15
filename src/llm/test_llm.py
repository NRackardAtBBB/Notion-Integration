
from config.settings import LLModel
from src.llm.model_factory import ModelFactory

def test_llm_processing():
    # Create model instance
    model = ModelFactory.create_model(
        model_type=LLModel.CLAUDE_SONNET,
        test_mode=True
    )
    
    # Process the input
    result = model.process_log_file()


if __name__ == "__main__":
    test_llm_processing()
