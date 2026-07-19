import json

async def parse_json_stream(token_stream):
    buffer = ''

    async for token in token_stream:
        buffer += token

        try:
            data = json.loads(buffer)
            yield data
            buffer=''
        except json.JSONDecodeError:
            continue