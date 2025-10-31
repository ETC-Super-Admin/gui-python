import re

def format_address_for_display(address: str) -> str:
    """
    Extracts sub-district (ตำบล) and province (จังหวัด) from a Thai address
    and formats it as 'sub-district / province'.

    Args:
        address: The full address string.

    Returns:
        The formatted string, or an empty string if parts are not found.
    """
    if not address or not isinstance(address, str):
        return ""

    # Regex to find sub-district (ต. or ตำบล.)
    tambon_pattern = re.compile(r'(?:ต\.|ตำบล\.)\s*(\S+)')
    # Regex to find province (จ. or จังหวัด.)
    changwat_pattern = re.compile(r'(?:จ\.|จังหวัด\.)\s*(\S+)')

    tambon_match = tambon_pattern.search(address)
    changwat_match = changwat_pattern.search(address)

    tambon = tambon_match.group(1) if tambon_match else ""
    changwat = changwat_match.group(1) if changwat_match else ""

    # Clean up potential trailing characters from the province name
    if changwat:
        changwat = changwat.split('Tel')[0].split('โทร')[0].strip()

    if tambon and changwat:
        return f"{tambon} / {changwat}"
    elif tambon:
        return tambon
    elif changwat:
        return changwat
    else:
        return ""
