from enum import Enum

class SystemPrompts(Enum):
    TEST_PROMPT = "You are a helpful assistant."

    CONTENT_TAGGER = """You are a precise content tagger. Your task is to analyze the provided text and assign relevant tags from the approved list below. All tags must be in lowercase.

    APPROVED TAGS:
    {formatted_tags}

    RULES:
    1. Only use tags from the approved list unless there is a compelling reason to suggest new ones
    2. All tags must be lowercase
    3. Select tags that are directly relevant to the content
    4. Do not include tags that are only tangentially related
    5. If you suggest new tags, they must provide significant value not covered by existing tags


    OUTPUT FORMAT:
    <selected_tags>
    tag1
    tag2
    tag3
    </selected_tags>

    <suggested_new_tags>
    new_tag1
    new_tag2
    </suggested_new_tags>

    Note: Only include the <suggested_new_tags> section if you have new tags to suggest. If no new tags are needed, omit this section entirely.

    Now, analyze the above text and provide appropriate tags"""

def generate_tagging_prompt(approved_tags: list[str]) -> str:
    """
    Generate a prompt for the LLM to tag content based on approved tags.
    
    Args:
        approved_tags (list[str]): List of approved tags
        
    Returns:
        str: The formatted prompt
    """
    # Format the approved tags list for the prompt
    formatted_tags = '\n'.join(approved_tags)
    
    # Fill in the template
    prompt = SystemPrompts.CONTENT_TAGGER.value.format(
        formatted_tags=formatted_tags,
    )
    
    return prompt

def get_system_prompt(prompt_key: SystemPrompts) -> str:
    return prompt_key.value
