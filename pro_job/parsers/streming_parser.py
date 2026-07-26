import json


async def parse_json_stream(token_stream):

    buffer = ""

    async for token in token_stream:

        buffer += token


        # Remove markdown code fences
        cleaned = (
            buffer
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )


        try:

            data = json.loads(cleaned)

            print("Valid JSON Received")

            yield data

            buffer = ""


        except json.JSONDecodeError:

            continue


    # Final attempt after stream finishes

    cleaned = (
        buffer
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )


    if cleaned:

        try:

            data = json.loads(cleaned)

            print("Valid JSON Received")

            yield data


        except json.JSONDecodeError:

            print("Warning: Stream ended with incomplete JSON")

            print("Raw output:")
            print(cleaned)