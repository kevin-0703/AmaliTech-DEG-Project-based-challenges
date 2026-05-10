import hashlib
import json
from decimal import Decimal


def normalize_data(data):
    normalized = {}

    for key, value in data.items():
        if isinstance(value, Decimal):
            normalized[key] = str(value)
        else:
            normalized[key] = value

    return normalized


def generate_request_hash(data):
    payload = normalize_data(data)
    serialized = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()