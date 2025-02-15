import re
from rapidfuzz import fuzz
from .tag_repository import load_approved_tags, add_approved_tag

def normalize_tag(tag: str) -> str:
    """
    Lowercase the tag, strip whitespace, replace dashes/underscores with a space,
    remove punctuation, and collapse multiple spaces.
    """
    normalized = tag.lower().strip()
    normalized = re.sub(r"[-_]+", " ", normalized)
    normalized = re.sub(r"[^\w\s]", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized

def sanitize_tags(tags: list[str], threshold: int = 90) -> list[str]:
    """
    Returns a list of tags sanitized according to a fuzzy matching threshold:
      - If the input tag closely matches any canonical tag (≥ threshold), 
        replace it with that canonical tag.
      - Otherwise, add the new normalized tag to the canonical list and use it.
    """
    canonical_tags = load_approved_tags()  # your existing known list of canonical tags
    sanitized_results = []

    for tag in tags:
        norm_tag = normalize_tag(tag)
        best_match = None
        highest_similarity = 0

        # Find the closest match in canonical_tags
        for canon in canonical_tags:
            similarity = fuzz.ratio(norm_tag, canon)
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = canon

        # Decide whether to reuse a canonical tag or create a new one
        if best_match and highest_similarity >= threshold:
            # Use existing canonical tag
            sanitized_results.append(best_match)
        else:
            # No close enough match, add this tag as new canonical
            add_approved_tag(norm_tag)
            canonical_tags.append(norm_tag)
            sanitized_results.append(norm_tag)

    # Return the new list of sanitized tags, mirroring the length/order of input
    return sanitized_results