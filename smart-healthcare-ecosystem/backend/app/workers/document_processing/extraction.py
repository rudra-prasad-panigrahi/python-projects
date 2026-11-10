import re
from .normalization import normalize_text

LAB_VALUE = re.compile(r"(?P<name>[A-Za-z][A-Za-z ]{1,40})\s*[:\-]\s*(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z/%]+)")
def extract_candidate_values(text: str) -> list[dict]:
    """Candidate extraction only; values require source review before clinical use."""
    return [m.groupdict() for m in LAB_VALUE.finditer(normalize_text(text))]
