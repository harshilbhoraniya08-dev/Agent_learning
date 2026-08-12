from typing import TypeVar, Type, Optional, AsyncGenerator
import asyncio
from openai import AsyncOpenAI
from pydantic import BaseModel
from core.config import config


# ==========================================================
# OpenRouter Client
# ==========================================================

client = AsyncOpenAI(
    api_key=config.OPENROUTER_API_KEY,
    base_url=config.BASE_URL,
)


# ==========================================================
# Generic Pydantic Type
# ==========================================================

T = TypeVar("T", bound=BaseModel)


# ==========================================================
# Normal LLM Call
# ==========================================================

async def call_llm(messages, output_model=None):
    """
    Send messages to the LLM.

    Parameters:
        messages: Chat messages
        output_model: Optional Pydantic model

    Returns:
        Pydantic model or string
    """

    response =  await client.chat.completions.create(
        model = config.MODEL,
        messages=messages,
        temperature=config.TEMPERATURE,
        max_tokens=config.MAX_TOKENS,
    )

    content = response.choices[0].message.content

    if output_model:
        return output_model.model_validate_json(content)
    
    return content