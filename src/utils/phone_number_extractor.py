import re
from typing import List

def extract_phone_numbers(text: str) -> str:
    """
    Extracts all 9 or 10-digit phone numbers from a given string.

    The regex looks for numbers starting with '0' followed by 8 or 9 digits,
    allowing for optional hyphens. It handles multiple numbers and returns
    them as a single comma-separated string.

    Args:
        text: The string to search for phone numbers.

    Returns:
        A string containing all found phone numbers, separated by a comma and space.
        Returns an empty string if no numbers are found.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Regex to find 10-digit numbers (0xx-xxx-xxxx) or 9-digit numbers (0x-xxx-xxxx)
    # It allows for hyphens but they are not required.
    phone_pattern = re.compile(r'\b(0\d{1,2}-?\d{3}-?\d{4})\b')
    
    found_numbers = phone_pattern.findall(text)
    
    # Join the found numbers into a single string
    return ", ".join(found_numbers)
