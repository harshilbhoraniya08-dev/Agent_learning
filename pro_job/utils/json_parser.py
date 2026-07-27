import json

def parse_json(text: str):

    text = text.strip()

    if text.startswith("```"):

        lines = text.splitlines()

        lines = lines[1:]

        if lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines)

    return json.loads(text)