import re

def parse_weight(raw):
    # Accept only stable readings
    if "ST" not in raw:
        return None

    match = re.search(r"(\d+(\.\d+)?)", raw)
    return float(match.group(1)) if match else None
