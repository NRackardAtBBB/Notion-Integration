def clean_rich_text(rich_text_list: list[dict]) -> str:
    """
    Given a list of rich_text objects from Notion (e.g. [{'text': {'content': 'Intro'}}]),
    returns a concatenated string of the inner content.
    """
    return "".join(
        item.get("text", {}).get("content", "") for item in rich_text_list
    )

def clean_multi_select(ms_list: list[dict]) -> list[str]:
    """
    Given a list of multi_select options (e.g.
    [{'name': 'UD'}, {'name': 'civic'}, ...]),
    returns a list of names.
    """
    return [item.get("name", "") for item in ms_list]

def clean_relation(rel_list: list[dict]) -> list[str]:
    """
    Given a list of relation objects (e.g.
    [{'id': 'test-id-7acba6af-80ae-4702-a3ed-8a59e56f12b5'}]),
    returns a list of ids.
    """
    return [item.get("id", "") for item in rel_list]

def clean_text_chunk_record(record: dict) -> dict:
    """
    Given a record (like the one being stored or retrieved for a TextChunk),
    clean its nested properties.
    For instance, if record['properties']['Title'] is a rich_text list,
    it returns the actual text string.
    """
    properties = record.get("properties", {})
    cleaned = {}
    for key, value in properties.items():
        if key == "Title" and isinstance(value, dict):
            # Check if it comes as rich_text or title
            if "rich_text" in value:
                cleaned[key] = clean_rich_text(value["rich_text"])
            elif "title" in value:
                cleaned[key] = clean_rich_text(value["title"])
            else:
                cleaned[key] = str(value)
        elif key == "Content" and isinstance(value, dict):
            cleaned[key] = clean_rich_text(value.get("rich_text", []))
        elif key == "Tags" and isinstance(value, dict):
            cleaned[key] = clean_multi_select(value.get("multi_select", []))
        elif key == "Project" and isinstance(value, dict):
            cleaned[key] = clean_relation(value.get("relation", []))
        else:
            cleaned[key] = value
    return cleaned
