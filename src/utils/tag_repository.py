import json
import os

DEFAULT_TAGS_FILE = os.path.join("data", "approved_tags.json")

def load_approved_tags(file_path: str = DEFAULT_TAGS_FILE) -> list[str]:
    """
    Loads the list of approved tags from the given JSON file.
    If the file doesn't exist, returns an empty list.
    """
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_approved_tags(tags: list[str], file_path: str = DEFAULT_TAGS_FILE) -> None:
    """
    Saves the provided list of approved tags into the given JSON file.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(tags, f, indent=2)

def add_approved_tag(new_tag: str, file_path: str = DEFAULT_TAGS_FILE) -> list[str]:
    """
    Adds a new approved tag to the repository, if it doesn't already exist.
    Returns the updated list of approved tags.
    """
    approved_tags = load_approved_tags(file_path)
    # Normalize new tag (here we could add a normalization step)
    normalized = new_tag.strip().lower()
    if normalized not in approved_tags:
        approved_tags.append(normalized)
        save_approved_tags(approved_tags, file_path)
    return approved_tags

def update_approved_tags(new_tags: list[str], file_path: str = DEFAULT_TAGS_FILE) -> list[str]:
    """
    Takes a list of new tags, normalizes them, merges them with the existing approved tags,
    removes duplicates, and updates the approved tags file.
    
    Args:
        new_tags: A list of new tag strings.
        file_path: Path to the approved tags JSON file (default is data/approved_tags.json).
    
    Returns:
        The updated list of approved tags.
    """
    # Load current approved tags and normalize them.
    current_tags = set(load_approved_tags(file_path))
    for tag in new_tags:
        normalized = tag.strip().lower()
        current_tags.add(normalized)
    updated_tags = sorted(list(current_tags))
    save_approved_tags(updated_tags, file_path)
    return updated_tags