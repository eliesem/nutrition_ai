def extract_between(text: str, start_marker: str, end_marker: str):
    """Extrait le texte entre deux marqueurs."""
    start = text.find(start_marker)
    if start == -1:
        return None
    start += len(start_marker)
    end = text.find(end_marker, start)
    if end == -1:
        return text[start:].strip()
    return text[start:end].strip()
