import asyncio
from model import SearchInput, SearchResult

async def search_tool(query: SearchInput):
    await asyncio.sleep(2)
    return {
        "articles":[
            "OpenAI announced new AI models",
            "Google released new AI research",
            "NVIDIA reported AI chip growth"
        ]
    }