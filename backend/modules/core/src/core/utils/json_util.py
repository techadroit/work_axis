import json


def parse_get_json(key: str, content):
    parsed_content = json.loads(content)
    value = parsed_content[key]
    return value
