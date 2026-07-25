import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
import json
from tools.tool_registery import TOOLS

load_dotenv()

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


async def call_llm(messages, output_model):
    responce = await client.chat.completions.create(
        model='openrouter/free',
        messages=messages,
        temperature=0.2,
        response_format={
            'type':'json_object'
        }

    )

    content = responce.choices[0].message.content

    data = json.loads(content)
    print("---------------------------------")
    print(content)
    print("---------------------------------")
    try:
        return output_model.model_validate(data)
    except Exception as e:
        print("Validation failed")
        print(data)
        raise e
    

async def stream_llm(messages):
    response = await client.chat.completions.create(
        model= "openrouter/free",
        messages=messages,
        temperature=0.2,
        stream=True
    )

    async for chunk in response:
        token = chunk.choices[0].delta.content

        if token:
            yield token

async def call_llm_with_tools(messages):
    response = await client.chat.completions.create(
        model= "openrouter/free",
        messages=messages,
        temperature=0.2,
        tools=TOOLS 
    )

    return response